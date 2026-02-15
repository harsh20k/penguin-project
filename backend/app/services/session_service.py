import secrets
from datetime import datetime
from app.db import get_connection


def create_session(user_id: str, factor1_done: bool = True) -> str:
    session_id = secrets.token_urlsafe(24)
    now = datetime.utcnow().isoformat() + "Z"
    conn = get_connection()
    conn.execute(
        """INSERT INTO sessions (session_id, user_id, factor1_done, factor2_done, factor3_done, created_at)
           VALUES (?, ?, ?, 0, 0, ?)""",
        (session_id, user_id, 1 if factor1_done else 0, now),
    )
    conn.commit()
    conn.close()
    return session_id


def set_factor2_done(session_id: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE sessions SET factor2_done = 1 WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def set_factor3_done(session_id: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE sessions SET factor3_done = 1 WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
