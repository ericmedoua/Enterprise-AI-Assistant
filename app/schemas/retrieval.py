from pydantic import BaseModel

from app.schemas.citation import Citation


class RetrievalResult(BaseModel):
    citation: Citation

    score: float
