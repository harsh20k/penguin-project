"""Issue and validate token after login. In-memory for local dev; DynamoDB when TOKEN_TABLE_NAME is set (Lambda)."""
import os
import secrets
import time
import boto3
from app.db import get_connection

# In-memory: token -> session_id (for local dev when TOKEN_TABLE_NAME not set).
_token_to_session: dict[str, str] = {}

TOKEN_TABLE_NAME = os.environ.get("TOKEN_TABLE_NAME") or os.environ.get("TOKEN_TABLE_NAME".upper())
SESSIONS_TABLE_NAME = os.environ.get("SESSIONS_TABLE_NAME") or os.environ.get("SESSIONS_TABLE_NAME".upper())

# Session token TTL in DynamoDB: 24 hours (seconds since epoch for TTL attribute).
TOKEN_TTL_SECONDS = 24 * 3600


def issue_token(session_id: str) -> str:
    token = secrets.token_urlsafe(32)
    if TOKEN_TABLE_NAME:
        ddb = boto3.client("dynamodb")
        ttl = int(time.time()) + TOKEN_TTL_SECONDS
        ddb.put_item(
            TableName=TOKEN_TABLE_NAME,
            Item={
                "token": {"S": token},
                "session_id": {"S": session_id},
                "ttl": {"N": str(ttl)},
            },
        )
    else:
        _token_to_session[token] = session_id
    return token


def resolve_token(token: str) -> str | None:
    if TOKEN_TABLE_NAME:
        ddb = boto3.client("dynamodb")
        resp = ddb.get_item(
            TableName=TOKEN_TABLE_NAME,
            Key={"token": {"S": token}},
        )
        item = resp.get("Item")
        if not item or "session_id" not in item:
            return None
        return item["session_id"].get("S")
    return _token_to_session.get(token)


def get_session_from_token(token: str) -> dict | None:
    """Return session row as dict if token valid and session exists."""
    session_id = resolve_token(token)
    if not session_id:
        return None
    if SESSIONS_TABLE_NAME:
        ddb = boto3.client("dynamodb")
        resp = ddb.get_item(
            TableName=SESSIONS_TABLE_NAME,
            Key={"session_id": {"S": session_id}},
        )
        item = resp.get("Item")
        if not item:
            return None
        return {
            "session_id": item["session_id"]["S"],
            "user_id": item["user_id"]["S"],
            "factor1_done": int(item.get("factor1_done", {}).get("N", "0")),
            "factor2_done": int(item.get("factor2_done", {}).get("N", "0")),
            "factor3_done": int(item.get("factor3_done", {}).get("N", "0")),
        }
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT session_id, user_id, factor1_done, factor2_done, factor3_done FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()
