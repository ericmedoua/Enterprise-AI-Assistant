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


@dataclass(frozen=True)
class EvaluationHistoryFilters:
    dataset_name: str | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    status: EvaluationStatus | None = None
    quality_gate_passed: bool | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
