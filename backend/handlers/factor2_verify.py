"""POST /auth/factor2/verify - require factor1, verify answer, set factor2 done."""
from app.lambda_utils import error_response, get_body_json, require_session, json_response
from app.services.factor2_service import verify_answer
from app.services.session_service import set_factor2_done


def handler(event, context):
    session, err = require_session(event, require_factor1=True)
    if err:
        return err
    body = get_body_json(event)
    if not body:
        return error_response("Invalid or missing body", 400)
    answer = body.get("answer")
    if answer is None:
        return error_response("answer required", 400)
    if not verify_answer(session["user_id"], answer):
        return error_response("Invalid answer", 403)
    set_factor2_done(session["session_id"])
    return json_response({"success": True})
