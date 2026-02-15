from pydantic import BaseModel


class Factor3ChallengeResponse(BaseModel):
    plaintext: str
    rotation: int


class Factor3VerifyRequest(BaseModel):
    ciphertext: str


class Factor3VerifyResponse(BaseModel):
    authenticated: bool
