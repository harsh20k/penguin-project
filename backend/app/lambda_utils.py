"""Shared helpers for API Gateway HTTP API v2 Lambda handlers."""
import json
from typing import Any

from app.auth.stub import get_session_from_token

CORS_HEADERS = {
    "content-type": "application/json",
    "access-control-allow-origin": "*",
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "*",
    "access-control-allow-headers": "*",
}


def get_headers(event: dict) -> dict:
    """Return request headers with lowercase keys."""
    raw = event.get("headers") or {}
    return {k.lower(): v for k, v in raw.items()}


def get_body_json(event: dict) -> dict | None:
    """Parse request body as JSON. Returns None if no body or invalid JSON."""
    body = event.get("body")
    if body is None:
        return None
    if isinstance(body, str):
        if not body.strip():
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None
    return body if isinstance(body, dict) else None


def get_auth_token(event: dict) -> str | None:
    """Extract Bearer token from Authorization header."""
    headers = get_headers(event)
    auth = headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        return None
    return auth[7:].strip()


def json_response(body: dict | list, status: int = 200) -> dict:
    """Build API Gateway HTTP API v2 response with CORS."""
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }


def error_response(message: str, status: int = 400) -> dict:
    """Build error response with detail message."""
    return json_response({"detail": message}, status=status)


def require_session(
    event: dict,
    require_factor1: bool = False,
    require_factor2: bool = False,
) -> tuple[dict[str, Any] | None, dict | None]:
    """
    Get session from Authorization token and optionally enforce factor progress.
    Returns (session, None) on success, or (None, error_response_dict) on failure.
    """
    token = get_auth_token(event)
    if not token:
        return None, error_response("Missing or invalid token", 401)
    session = get_session_from_token(token)
    if not session:
        return None, error_response("Invalid or expired token", 401)
    if require_factor1 and not session.get("factor1_done"):
        return None, error_response("Factor 1 not completed", 403)
    if require_factor2:
        if not session.get("factor1_done"):
            return None, error_response("Factor 1 not completed", 403)
        if not session.get("factor2_done"):
            return None, error_response("Factor 2 not completed", 403)
    return session, None
