from pydantic import BaseModel
from app.schemas.citation import Citation


class ChatSessionCreate(BaseModel):
    title: str | None = "New Chat"


class ChatSessionRename(BaseModel):
    title: str


class ChatQuestion(BaseModel):
    question: str


class ChatSessionResponse(BaseModel):
    id: int
    title: str

    model_config = {"from_attributes": True}


class ChatAnswer(BaseModel):
    answer: str

    citations: list[Citation]
