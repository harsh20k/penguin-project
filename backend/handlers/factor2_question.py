"""GET /auth/factor2/question - require factor1, return security question."""
from app.lambda_utils import error_response, require_session, json_response
from app.services.factor2_service import get_question_for_user


def handler(event, context):
    session, err = require_session(event, require_factor1=True)
    if err:
        return err
    question = get_question_for_user(session["user_id"])
    if not question:
        return error_response("No security question set", 404)
    return json_response({"question": question})
