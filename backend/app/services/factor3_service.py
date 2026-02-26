"""Factor 3: Caesar challenge – generate challenge, verify cipher (constant-time)."""
import random
import string
from datetime import datetime


from app.db import get_connection
from app.services.caesar import caesar_encode, constant_time_compare
from app.aws_integration import get_user_mfa_config


def _random_plaintext(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def get_or_create_challenge(session_id: str, user_id: str) -> str:
    """Return the plaintext challenge for this session.

    The user's Caesar rotation key is looked up from their MFA config (set at
    registration) and used to pre-compute the expected ciphertext. The rotation
    is NOT returned to the caller — the user must apply their own key.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT plaintext FROM caesar_challenges WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if row:
        conn.close()
        return row["plaintext"]

    cfg = get_user_mfa_config(user_id)
    if not cfg:
        conn.close()
        raise ValueError(f"No MFA config found for user {user_id}")
    rotation = cfg.rotation

    plaintext = _random_plaintext()
    expected = caesar_encode(plaintext, rotation)
    now = datetime.utcnow().isoformat() + "Z"
    conn.execute(
        """INSERT OR REPLACE INTO caesar_challenges
               (session_id, plaintext, rotation, expected_ciphertext, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (session_id, plaintext, rotation, expected, now),
    )
    conn.commit()
    conn.close()
    return plaintext


def verify_cipher(session_id: str, ciphertext: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT expected_ciphertext FROM caesar_challenges WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()
    if not row:
        return False
    return constant_time_compare(ciphertext.strip(), row["expected_ciphertext"])
