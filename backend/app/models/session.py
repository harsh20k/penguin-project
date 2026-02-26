from pydantic import BaseModel, field_validator


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


class SignupRequest(BaseModel):
    email: str
    password: str
    role: str | None = "client"
    question: str | None = "What is your favorite color?"
    answer: str | None = "blue"
    rotation: int = 7  # Caesar cipher key (1–25), provided by user at registration

    @field_validator("rotation")
    @classmethod
    def rotation_in_range(cls, v: int) -> int:
        if not 1 <= v <= 25:
            raise ValueError("rotation must be between 1 and 25")
        return v
