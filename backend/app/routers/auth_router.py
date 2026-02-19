import json
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_session, require_factor1, require_factor2
from app.auth.stub import issue_token
from app.models.session import LoginRequest, LoginResponse, SessionResponse, SignupRequest
from app.models.factor2 import Factor2QuestionResponse, Factor2VerifyRequest, Factor2VerifyResponse
from app.models.factor3 import Factor3ChallengeResponse, Factor3VerifyRequest, Factor3VerifyResponse
from app.services.session_service import create_session, set_factor2_done, set_factor3_done
from app.services.factor2_service import get_question_for_user, verify_answer
from app.services.factor3_service import get_or_create_challenge, verify_cipher
from app.aws_integration import signup_user, cognito_login, get_cognito_user_id
from app.db import get_connection
from passlib.context import CryptContext

router = APIRouter()
pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
# #region agent log
_DEBUG_LOG_PATH = Path(__file__).resolve().parents[3] / ".cursor" / "debug-636235.log"
def _debug_log(loc: str, msg: str, data: dict, hid: str):
    try:
        with open(_DEBUG_LOG_PATH, "a") as f:
            f.write(json.dumps({"sessionId": "636235", "location": loc, "message": msg, "data": data, "timestamp": int(time.time() * 1000), "hypothesisId": hid}) + "\n")
    except Exception:
        pass
# #endregion


@router.post("/signup")
def signup(req: SignupRequest):
    """
    Create a Cognito user and store MFA configuration in DynamoDB.
    """
    try:
        answer = req.answer or "blue"
        question = req.question or "What is your favorite color?"
        role = req.role or "client"
        rotation = req.rotation or 7

        answer_hash = pwd_ctx.hash(answer)
        user_id = signup_user(
            email=req.email,
            password=req.password,
            role=role,
            question=question,
            answer_hash=answer_hash,
            rotation=rotation,
        )
    except Exception as exc:  # pragma: no cover - surface AWS errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {exc}",
        ) from exc

    # #region agent log
    from app.aws_integration import DDB_USER_TABLE_NAME
    _debug_log("auth_router.py:signup", "signup stored MFA", {"user_id": user_id, "DDB_USER_TABLE_NAME": DDB_USER_TABLE_NAME or "(none)"}, "B")
    # #endregion
    return {"user_id": user_id}


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Factor 1: username (email) + password via Cognito -> session + token.

    On success, we start a local session keyed by Cognito user and return a
    dev token that the frontend uses for subsequent factor 2/3 calls.
    """
    try:
        auth_result = cognito_login(req.username.strip(), req.password)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Use Cognito sub as user_id so factor2/factor3 find MFA data (stored by sub at signup).
    user_id = get_cognito_user_id(auth_result["AccessToken"])
    session_id = create_session(user_id, factor1_done=True)
    token = issue_token(session_id)
    return LoginResponse(
        session_id=session_id,
        token=token,
        id_token=auth_result.get("IdToken"),
        access_token=auth_result.get("AccessToken"),
    )


@router.post("/session", response_model=SessionResponse)
def create_session_endpoint():
    """Real flow: after Cognito, create session. Local: use POST /auth/login instead."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use POST /auth/login for local dev",
    )


@router.get("/factor2/question", response_model=Factor2QuestionResponse)
def get_factor2_question(session: dict = Depends(require_factor1)):
    user_id = session["user_id"]
    question = get_question_for_user(user_id)
    # #region agent log
    from app.aws_integration import DDB_USER_TABLE_NAME as _tbl
    _debug_log("auth_router.py:get_factor2_question", "factor2 lookup", {"user_id": user_id, "question_found": question is not None, "session_id": session.get("session_id"), "DDB_USER_TABLE_NAME": _tbl or "(none)"}, "B")
    # #endregion
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No security question set")
    return Factor2QuestionResponse(question=question)


@router.post("/factor2/verify", response_model=Factor2VerifyResponse)
def verify_factor2(req: Factor2VerifyRequest, session: dict = Depends(require_factor1)):
    session_id = session["session_id"]
    user_id = session["user_id"]
    if not verify_answer(user_id, req.answer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid answer")
    set_factor2_done(session_id)
    return Factor2VerifyResponse(success=True)


@router.get("/factor3/challenge", response_model=Factor3ChallengeResponse)
def get_factor3_challenge(session: dict = Depends(require_factor2)):
    session_id = session["session_id"]
    user_id = session["user_id"]
    plaintext, rotation = get_or_create_challenge(session_id, user_id)
    return Factor3ChallengeResponse(plaintext=plaintext, rotation=rotation)


@router.post("/factor3/verify", response_model=Factor3VerifyResponse)
def verify_factor3(req: Factor3VerifyRequest, session: dict = Depends(require_factor2)):
    session_id = session["session_id"]
    if not verify_cipher(session_id, req.ciphertext):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid cipher answer")
    set_factor3_done(session_id)
    return Factor3VerifyResponse(authenticated=True)
