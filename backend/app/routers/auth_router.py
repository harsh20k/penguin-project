from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_session, require_factor1, require_factor2
from app.auth.stub import issue_token
from app.models.session import LoginRequest, LoginResponse, SessionResponse
from app.models.factor2 import Factor2QuestionResponse, Factor2VerifyRequest, Factor2VerifyResponse
from app.models.factor3 import Factor3ChallengeResponse, Factor3VerifyRequest, Factor3VerifyResponse
from app.services.session_service import create_session, set_factor2_done, set_factor3_done
from app.db import get_connection
from passlib.context import CryptContext

router = APIRouter()
pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """Dev stub: username (email) + password -> session + token."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, password_hash FROM users WHERE email = ?", (req.username.strip(),)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    user_id = row["id"]
    password_hash = row["password_hash"]
    if not password_hash or not pwd_ctx.verify(req.password, password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    session_id = create_session(user_id, factor1_done=True)
    token = issue_token(session_id)
    return LoginResponse(session_id=session_id, token=token)


@router.post("/session", response_model=SessionResponse)
def create_session_endpoint():
    """Real flow: after Cognito, create session. Local: use POST /auth/login instead."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use POST /auth/login for local dev",
    )


@router.get("/factor2/question", response_model=Factor2QuestionResponse)
def get_factor2_question(session: dict = Depends(require_factor1)):
    from app.services.factor2_service import get_question_for_user
    user_id = session["user_id"]
    question = get_question_for_user(user_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No security question set")
    return Factor2QuestionResponse(question=question)


@router.post("/factor2/verify", response_model=Factor2VerifyResponse)
def verify_factor2(req: Factor2VerifyRequest, session: dict = Depends(require_factor1)):
    from app.services.factor2_service import verify_answer
    session_id = session["session_id"]
    user_id = session["user_id"]
    if not verify_answer(user_id, req.answer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid answer")
    set_factor2_done(session_id)
    return Factor2VerifyResponse(success=True)


@router.get("/factor3/challenge", response_model=Factor3ChallengeResponse)
def get_factor3_challenge(session: dict = Depends(require_factor2)):
    from app.services.factor3_service import get_or_create_challenge
    session_id = session["session_id"]
    user_id = session["user_id"]
    plaintext, rotation = get_or_create_challenge(session_id, user_id)
    return Factor3ChallengeResponse(plaintext=plaintext, rotation=rotation)


@router.post("/factor3/verify", response_model=Factor3VerifyResponse)
def verify_factor3(req: Factor3VerifyRequest, session: dict = Depends(require_factor2)):
    from app.services.factor3_service import verify_cipher
    session_id = session["session_id"]
    if not verify_cipher(session_id, req.ciphertext):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid cipher answer")
    set_factor3_done(session_id)
    return Factor3VerifyResponse(authenticated=True)
