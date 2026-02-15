"""Dev-only: issue and validate token after login. Token maps to session_id."""
import secrets
from app.db import get_connection

# In-memory: token -> session_id (for dev). Could use DB table instead.
_token_to_session: dict[str, str] = {}


def issue_token(session_id: str) -> str:
    token = secrets.token_urlsafe(32)
    _token_to_session[token] = session_id
    return token


def resolve_token(token: str) -> str | None:
    return _token_to_session.get(token)


def get_session_from_token(token: str) -> dict | None:
    """Return session row as dict if token valid and session exists."""
    session_id = resolve_token(token)
    if not session_id:
        return None
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
