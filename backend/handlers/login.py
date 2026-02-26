"""POST /auth/login - Factor 1: Cognito auth, create session, return token."""
from app.aws_integration import cognito_login, get_cognito_user_id
from app.auth.stub import issue_token
from app.lambda_utils import error_response, get_body_json, json_response
from app.services.session_service import create_session


def handler(event, context):
    body = get_body_json(event)
    if not body:
        return error_response("Invalid or missing body", 400)
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return error_response("username and password required", 400)
    try:
        auth_result = cognito_login(username.strip(), password)
    except Exception:
        return error_response("Invalid credentials", 401)
    user_id = get_cognito_user_id(auth_result["AccessToken"])
    session_id = create_session(user_id, factor1_done=True)
    token = issue_token(session_id)
    return json_response({
        "session_id": session_id,
        "token": token,
        "id_token": auth_result.get("IdToken"),
        "access_token": auth_result.get("AccessToken"),
    })
