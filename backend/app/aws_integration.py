from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.client import BaseClient


COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID") or os.environ.get("COGNITO_USER_POOL_ID".upper())
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID") or os.environ.get("COGNITO_CLIENT_ID".upper())
DDB_USER_TABLE_NAME = os.environ.get("DDB_USER_TABLE_NAME") or os.environ.get("DDB_USER_TABLE_NAME".upper())


def _cognito() -> BaseClient:
    return boto3.client("cognito-idp")


def _dynamodb() -> BaseClient:
    return boto3.client("dynamodb")


@dataclass
class UserMfaConfig:
    user_id: str
    role: str
    question: str
    answer_hash: str
    rotation: int


def signup_user(
    email: str,
    password: str,
    role: str,
    question: str,
    answer_hash: str,
    rotation: int,
) -> str:
    """
    Create user in Cognito and store MFA metadata in DynamoDB.

    Returns the Cognito user sub (user_id).
    """
    if not COGNITO_USER_POOL_ID or not COGNITO_CLIENT_ID or not DDB_USER_TABLE_NAME:
        raise RuntimeError("Cognito/DynamoDB environment not configured")

    cognito = _cognito()

    # Create user and set password
    resp = cognito.admin_create_user(
        UserPoolId=COGNITO_USER_POOL_ID,
        Username=email,
        UserAttributes=[{"Name": "email", "Value": email}],
        MessageAction="SUPPRESS",
    )
    username = resp["User"]["Username"]

    cognito.admin_set_user_password(
        UserPoolId=COGNITO_USER_POOL_ID,
        Username=username,
        Password=password,
        Permanent=True,
    )

    # Fetch sub (user_id)
    user = cognito.admin_get_user(UserPoolId=COGNITO_USER_POOL_ID, Username=username)
    sub_attr = next(a for a in user["UserAttributes"] if a["Name"] == "sub")
    user_id = sub_attr["Value"]

    # Store MFA metadata in DynamoDB
    ddb = _dynamodb()
    ddb.put_item(
        TableName=DDB_USER_TABLE_NAME,
        Item={
            "user_id": {"S": user_id},
            "email": {"S": email},
            "role": {"S": role},
            "question": {"S": question},
            "answer_hash": {"S": answer_hash},
            "rotation": {"N": str(rotation)},
        },
    )

    return user_id


def cognito_login(email: str, password: str) -> dict:
    """
    Perform Cognito auth and return auth result including tokens.
    """
    if not COGNITO_CLIENT_ID:
        raise RuntimeError("COGNITO_CLIENT_ID not configured")

    cognito = _cognito()
    resp = cognito.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": email,
            "PASSWORD": password,
        },
        ClientId=COGNITO_CLIENT_ID,
    )
    return resp["AuthenticationResult"]


def get_cognito_user_id(access_token: str) -> str:
    """
    Resolve Cognito user sub (user_id) from Access Token.
    """
    cognito = _cognito()
    user = cognito.get_user(AccessToken=access_token)
    sub_attr = next(a for a in user["UserAttributes"] if a["Name"] == "sub")
    return sub_attr["Value"]


def get_user_mfa_config(user_id: str) -> Optional[UserMfaConfig]:
    """
    Fetch MFA configuration for a user from DynamoDB.
    """
    if not DDB_USER_TABLE_NAME:
        raise RuntimeError("DDB_USER_TABLE_NAME not configured")

    ddb = _dynamodb()
    resp = ddb.get_item(
        TableName=DDB_USER_TABLE_NAME,
        Key={"user_id": {"S": user_id}},
    )
    item = resp.get("Item")
    if not item:
        return None

    return UserMfaConfig(
        user_id=user_id,
        role=item.get("role", {}).get("S", "client"),
        question=item.get("question", {}).get("S", ""),
        answer_hash=item.get("answer_hash", {}).get("S", ""),
        rotation=int(item.get("rotation", {}).get("N", "7")),
    )

