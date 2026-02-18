from pydantic import BaseModel


class Factor2QuestionResponse(BaseModel):
    question: str


class Factor2VerifyRequest(BaseModel):
    answer: str


class Factor2VerifyResponse(BaseModel):
    success: bool
