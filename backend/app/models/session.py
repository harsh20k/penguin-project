from pydantic import BaseModel


class SessionCreate(BaseModel):
    pass  # Real: cognito token. Dev: session created via /auth/login


class SessionResponse(BaseModel):
    session_id: str
    token: str | None = None


class LoginRequest(BaseModel):
    username: str  # email for dev
    password: str


class LoginResponse(BaseModel):
    session_id: str
    token: str
    id_token: str | None = None
    access_token: str | None = None
