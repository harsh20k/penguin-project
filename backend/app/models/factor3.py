from pydantic import BaseModel


class Factor3ChallengeResponse(BaseModel):
    plaintext: str
    # rotation is intentionally omitted — the user already knows their key from registration


class Factor3VerifyRequest(BaseModel):
    ciphertext: str


class Factor3VerifyResponse(BaseModel):
    authenticated: bool
