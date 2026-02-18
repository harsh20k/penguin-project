"""Seed one dev user with security Q&A and Caesar config for local 3FA flow."""
import os
import sys
from pathlib import Path

# Run from backend/
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DB_PATH", str(Path(__file__).resolve().parent / "local.db"))

from app.db import init_db, get_connection
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

DEV_USER_ID = "dev-user-00000000-0000-0000-0000-000000000001"
DEV_EMAIL = "dev@local"
DEV_PASSWORD = "devpass"
DEV_ROLE = "client"
SECURITY_QUESTION = "What is your favorite color?"
SECURITY_ANSWER = "blue"
CAESAR_ROTATION = 7


def main():
    init_db()
    user_id = DEV_USER_ID

    password_hash = pwd_ctx.hash(DEV_PASSWORD)
    answer_hash = pwd_ctx.hash(SECURITY_ANSWER)

    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO users (id, email, role, password_hash) VALUES (?, ?, ?, ?)",
        (user_id, DEV_EMAIL, DEV_ROLE, password_hash),
    )
    conn.execute(
        """INSERT OR REPLACE INTO security_qa (user_id, question_id, question, answer_hash)
           VALUES (?, 'q1', ?, ?)""",
        (user_id, SECURITY_QUESTION, answer_hash),
    )
    conn.execute(
        "INSERT OR REPLACE INTO caesar_config (user_id, rotation) VALUES (?, ?)",
        (user_id, CAESAR_ROTATION),
    )
    conn.commit()
    conn.close()

    print("Seeded dev user:")
    print(f"  email: {DEV_EMAIL}")
    print(f"  password: {DEV_PASSWORD}")
    print(f"  security Q: {SECURITY_QUESTION}")
    print(f"  security A: {SECURITY_ANSWER}")
    print(f"  Caesar rotation: {CAESAR_ROTATION}")


if __name__ == "__main__":
    main()

