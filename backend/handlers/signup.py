"""POST /auth/signup - create Cognito user and store MFA config."""
from passlib.context import CryptContext

from app.aws_integration import signup_user
from app.lambda_utils import error_response, get_body_json, json_response

pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def handler(event, context):
    body = get_body_json(event)
    if not body:
        return error_response("Invalid or missing body", 400)
    email = body.get("email")
    password = body.get("password")
    if not email or not password:
        return error_response("email and password required", 400)
    question = body.get("question") or "What is your favorite color?"
    answer = body.get("answer") or "blue"
    role = body.get("role") or "client"
    rotation = body.get("rotation")
    if rotation is None:
        rotation = 7
    try:
        rotation = int(rotation)
    except (TypeError, ValueError):
        rotation = 7
    answer_hash = pwd_ctx.hash(answer)
    try:
        user_id = signup_user(
            email=email.strip(),
            password=password,
            role=role,
            question=question,
            answer_hash=answer_hash,
            rotation=rotation,
        )
    except Exception as exc:
        return error_response(f"Signup failed: {exc}", 400)
    return json_response({"user_id": user_id})
