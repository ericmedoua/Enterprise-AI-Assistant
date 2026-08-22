from dataclasses import dataclass

from app.core.config import settings
from app.core.git_metadata import get_git_commit


@dataclass(frozen=True)
class EvaluationMetadata:
    llm_model: str
    embedding_model: str
    git_commit: str


def get_evaluation_metadata() -> EvaluationMetadata:
    return EvaluationMetadata(
        llm_model=settings.GROQ_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        git_commit=get_git_commit(),
    )
