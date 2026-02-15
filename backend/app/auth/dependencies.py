from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.stub import get_session_from_token

security = HTTPBearer(auto_error=False)


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")
    return credentials.credentials


def get_session(token: str = Depends(get_current_token)) -> dict:
    session = get_session_from_token(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return session


def require_factor1(session: dict = Depends(get_session)) -> dict:
    if not session.get("factor1_done"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Factor 1 not completed")
    return session


def require_factor2(session: dict = Depends(get_session)) -> dict:
    if not session.get("factor1_done"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Factor 1 not completed")
    if not session.get("factor2_done"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Factor 2 not completed")
    return session
