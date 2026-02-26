"""Factor 3: Caesar challenge – generate challenge, verify cipher (constant-time).

Challenges are stored in DynamoDB (CHALLENGES_TABLE_NAME) so they survive
across Lambda instances. Falls back to SQLite for local dev (no env var set).
"""
import os
import random
import string
from datetime import datetime, timezone

from app.services.caesar import caesar_encode, constant_time_compare
from app.aws_integration import get_user_mfa_config

CHALLENGES_TABLE_NAME = os.environ.get("CHALLENGES_TABLE_NAME")
CHALLENGE_TTL_SECONDS = 600  # 10 minutes


def _random_plaintext(length: int = 4) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def _now_epoch() -> int:
    return int(datetime.now(timezone.utc).timestamp())


# ── DynamoDB path ────────────────────────────────────────────────────────────

def _ddb_get_challenge(session_id: str) -> dict | None:
    import boto3
    ddb = boto3.client("dynamodb")
    resp = ddb.get_item(
        TableName=CHALLENGES_TABLE_NAME,
        Key={"session_id": {"S": session_id}},
        ConsistentRead=True,
    )
    return resp.get("Item")


def _ddb_put_challenge(session_id: str, plaintext: str, expected: str) -> None:
    import boto3
    ddb = boto3.client("dynamodb")
    ttl = _now_epoch() + CHALLENGE_TTL_SECONDS
    ddb.put_item(
        TableName=CHALLENGES_TABLE_NAME,
        Item={
            "session_id":          {"S": session_id},
            "plaintext":           {"S": plaintext},
            "expected_ciphertext": {"S": expected},
            "ttl":                 {"N": str(ttl)},
        },
        ConditionExpression="attribute_not_exists(session_id)",
    )


def _ddb_get_expected(session_id: str) -> str | None:
    item = _ddb_get_challenge(session_id)
    if not item:
        return None
    return item["expected_ciphertext"]["S"]


# ── SQLite fallback (local dev) ──────────────────────────────────────────────

def _sqlite_get_challenge(session_id: str) -> dict | None:
    from app.db import get_connection
    conn = get_connection()
    row = conn.execute(
        "SELECT plaintext, expected_ciphertext FROM caesar_challenges WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _sqlite_put_challenge(session_id: str, plaintext: str, expected: str) -> None:
    from app.db import get_connection
    conn = get_connection()
    now = datetime.utcnow().isoformat() + "Z"
    conn.execute(
        """INSERT OR IGNORE INTO caesar_challenges
               (session_id, plaintext, rotation, expected_ciphertext, created_at)
           VALUES (?, ?, 0, ?, ?)""",
        (session_id, plaintext, expected, now),
    )
    conn.commit()
    conn.close()


def _sqlite_get_expected(session_id: str) -> str | None:
    row = _sqlite_get_challenge(session_id)
    return row["expected_ciphertext"] if row else None


# ── Public API ───────────────────────────────────────────────────────────────

def get_or_create_challenge(session_id: str, user_id: str) -> str:
    """Return the plaintext challenge for this session (4 chars).

    Looks up the user's rotation from DynamoDB MFA config (set at registration)
    and pre-computes the expected ciphertext. The rotation is NOT returned to
    the caller — the user applies their own key.
    """
    use_ddb = bool(CHALLENGES_TABLE_NAME)

    # Return existing challenge if already created for this session
    if use_ddb:
        existing = _ddb_get_challenge(session_id)
        if existing:
            return existing["plaintext"]["S"]
    else:
        existing = _sqlite_get_challenge(session_id)
        if existing:
            return existing["plaintext"]

    cfg = get_user_mfa_config(user_id)
    if not cfg:
        raise ValueError(f"No MFA config found for user {user_id}")

    plaintext = _random_plaintext(length=4)
    expected = caesar_encode(plaintext, cfg.rotation)

    try:
        if use_ddb:
            _ddb_put_challenge(session_id, plaintext, expected)
        else:
            _sqlite_put_challenge(session_id, plaintext, expected)
    except Exception:
        # Race condition: another instance already wrote it; fetch and return that one
        if use_ddb:
            existing = _ddb_get_challenge(session_id)
            if existing:
                return existing["plaintext"]["S"]
        else:
            existing = _sqlite_get_challenge(session_id)
            if existing:
                return existing["plaintext"]
        raise

    return plaintext


def verify_cipher(session_id: str, ciphertext: str) -> bool:
    if CHALLENGES_TABLE_NAME:
        expected = _ddb_get_expected(session_id)
    else:
        expected = _sqlite_get_expected(session_id)

    if not expected:
        return False
    return constant_time_compare(ciphertext.strip(), expected)
