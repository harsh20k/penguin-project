"""POST /auth/factor3/verify - require factor2, verify cipher, set factor3 done."""
from app.db import init_db
from app.lambda_utils import error_response, get_body_json, require_session, json_response
from app.services.factor3_service import verify_cipher
from app.services.session_service import set_factor3_done

# Ensure SQLite tables exist for caesar_challenges (Lambda uses /tmp DB).
init_db()


def handler(event, context):
    session, err = require_session(event, require_factor2=True)
    if err:
        return err
    body = get_body_json(event)
    if not body:
        return error_response("Invalid or missing body", 400)
    ciphertext = body.get("ciphertext")
    if ciphertext is None:
        return error_response("ciphertext required", 400)
    if not verify_cipher(session["session_id"], ciphertext):
        return error_response("Invalid cipher answer", 403)
    set_factor3_done(session["session_id"])
    return json_response({"authenticated": True})
