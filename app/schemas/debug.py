from pydantic import BaseModel


class RetrievalDebugResult(BaseModel):
    score: float

    source: str

    page: int | None = None

    chunk: int | None = None

    preview: str


class RetrievalDebugResponse(BaseModel):
    query: str

    results: list[RetrievalDebugResult]
