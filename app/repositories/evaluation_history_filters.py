from dataclasses import dataclass
from datetime import datetime
from typing import Literal

EvaluationStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
    "cancelled",
]

EvaluationHistorySortField = Literal[
    "created_at",
    "total_cases",
    "retrieval_hit_rate",
    "average_groundedness",
    "average_semantic_relevance",
    "overall_pass_rate",
]

EvaluationHistorySortOrder = Literal[
    "asc",
    "desc",
]


@dataclass(frozen=True)
class EvaluationHistoryFilters:
    dataset_name: str | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    status: EvaluationStatus | None = None
    quality_gate_passed: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
