from pydantic import BaseModel


class SourceDocument(BaseModel):
    source: str
    page: int | None = None
    score: float | None = None
