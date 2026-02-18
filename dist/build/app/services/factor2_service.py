"""Factor 2: security Q&A backed by DynamoDB user_mfa table."""
from passlib.context import CryptContext

from app.aws_integration import get_user_mfa_config

pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def get_question_for_user(user_id: str) -> str | None:
    cfg = get_user_mfa_config(user_id)
    return cfg.question if cfg else None


def verify_answer(user_id: str, answer: str) -> bool:
    cfg = get_user_mfa_config(user_id)
    if not cfg:
        return False
    try:
        return pwd_ctx.verify(answer, cfg.answer_hash)
    except Exception:
        return False
