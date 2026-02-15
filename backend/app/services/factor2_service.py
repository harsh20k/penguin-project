"""Factor 2: security Q&A – get question, verify answer (hashed, constant-time)."""
import secrets
from app.db import get_connection
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_question_for_user(user_id: str) -> str | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT question FROM security_qa WHERE user_id = ? LIMIT 1", (user_id,)
    ).fetchone()
    conn.close()
    return row["question"] if row else None


def verify_answer(user_id: str, answer: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT answer_hash FROM security_qa WHERE user_id = ? LIMIT 1", (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return False
    # bcrypt verify is constant-time; use it for comparison
    try:
        return pwd_ctx.verify(answer, row["answer_hash"])
    except Exception:
        return False
