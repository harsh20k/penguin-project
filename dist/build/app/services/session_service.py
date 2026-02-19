import os
import secrets
from datetime import datetime

import boto3
from app.db import get_connection

SESSIONS_TABLE_NAME = os.environ.get("SESSIONS_TABLE_NAME") or os.environ.get("SESSIONS_TABLE_NAME".upper())


def create_session(user_id: str, factor1_done: bool = True) -> str:
    session_id = secrets.token_urlsafe(24)
    f1 = 1 if factor1_done else 0
    if SESSIONS_TABLE_NAME:
        ddb = boto3.client("dynamodb")
        ddb.put_item(
            TableName=SESSIONS_TABLE_NAME,
            Item={
                "session_id": {"S": session_id},
                "user_id": {"S": user_id},
                "factor1_done": {"N": str(f1)},
                "factor2_done": {"N": "0"},
                "factor3_done": {"N": "0"},
            },
        )
    else:
        now = datetime.utcnow().isoformat() + "Z"
        conn = get_connection()
        conn.execute(
            """INSERT INTO sessions (session_id, user_id, factor1_done, factor2_done, factor3_done, created_at)
               VALUES (?, ?, ?, 0, 0, ?)""",
            (session_id, user_id, f1, now),
        )
        conn.commit()
        conn.close()
    return session_id


def set_factor2_done(session_id: str) -> None:
    if SESSIONS_TABLE_NAME:
        boto3.client("dynamodb").update_item(
            TableName=SESSIONS_TABLE_NAME,
            Key={"session_id": {"S": session_id}},
            UpdateExpression="SET factor2_done = :d",
            ExpressionAttributeValues={":d": {"N": "1"}},
        )
    else:
        conn = get_connection()
        conn.execute("UPDATE sessions SET factor2_done = 1 WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()


def set_factor3_done(session_id: str) -> None:
    if SESSIONS_TABLE_NAME:
        boto3.client("dynamodb").update_item(
            TableName=SESSIONS_TABLE_NAME,
            Key={"session_id": {"S": session_id}},
            UpdateExpression="SET factor3_done = :d",
            ExpressionAttributeValues={":d": {"N": "1"}},
        )
    else:
        conn = get_connection()
        conn.execute("UPDATE sessions SET factor3_done = 1 WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
