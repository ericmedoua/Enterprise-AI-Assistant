from pydantic import BaseModel


class Citation(BaseModel):
    source: str

    page: int | None = None

    chunk: int | None = None
