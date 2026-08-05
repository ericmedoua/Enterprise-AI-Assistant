from pydantic import BaseModel

from app.schemas.source import SourceDocument


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
