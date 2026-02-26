"""GET /auth/factor3/challenge - require factor2, return plaintext challenge.

The user applies their own Caesar key (set at registration) to the plaintext
and submits the resulting ciphertext to POST /auth/factor3/verify.
"""
from app.db import init_db
from app.lambda_utils import error_response, require_session, json_response
from app.services.factor3_service import get_or_create_challenge

# Ensure SQLite tables exist for caesar_challenges (Lambda uses /tmp DB).
init_db()


def handler(event, context):
    session, err = require_session(event, require_factor2=True)
    if err:
        return err
    try:
        plaintext = get_or_create_challenge(session["session_id"], session["user_id"])
    except ValueError as exc:
        return error_response(str(exc), 404)
    return json_response({"plaintext": plaintext})
