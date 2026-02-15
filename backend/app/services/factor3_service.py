"""Factor 3: Caesar challenge – generate challenge, verify cipher (constant-time)."""
import random
import string
from datetime import datetime
from app.db import get_connection
from app.services.caesar import caesar_encode, constant_time_compare


def _random_plaintext(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def get_or_create_challenge(session_id: str, user_id: str) -> tuple[str, int]:
    conn = get_connection()
    row = conn.execute(
        "SELECT plaintext, rotation, expected_ciphertext FROM caesar_challenges WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if row:
        conn.close()
        return row["plaintext"], row["rotation"]
    # Get user's default rotation or random
    cfg = conn.execute("SELECT rotation FROM caesar_config WHERE user_id = ?", (user_id,)).fetchone()
    rotation = cfg["rotation"] if cfg else random.randint(1, 25)
    plaintext = _random_plaintext()
    expected = caesar_encode(plaintext, rotation)
    now = datetime.utcnow().isoformat() + "Z"
    conn.execute(
        """INSERT OR REPLACE INTO caesar_challenges (session_id, plaintext, rotation, expected_ciphertext, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (session_id, plaintext, rotation, expected, now),
    )
    conn.commit()
    conn.close()
    return plaintext, rotation


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
