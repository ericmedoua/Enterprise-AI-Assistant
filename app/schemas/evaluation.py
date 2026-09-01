from datetime import datetime

from pydantic import BaseModel


class EvaluationRunResponse(BaseModel):
    id: int
    created_at: datetime
    dataset_name: str

    llm_model: str
    embedding_model: str
    git_commit: str

    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None

    total_cases: int
    retrieval_hit_rate: float
    average_groundedness: float
    average_semantic_relevance: float
    average_source_count: float
    overall_pass_rate: float

    quality_gate_passed: bool


class EvaluationHistoryResponse(BaseModel):
    runs: list[EvaluationRunResponse]


class EvaluationComparisonResponse(BaseModel):
    retrieval_hit_rate_delta: float
    groundedness_delta: float
    semantic_relevance_delta: float
    source_count_delta: float
    overall_pass_rate_delta: float


class EvaluationSnapshotResponse(BaseModel):
    dataset_name: str
    report: dict
    quality_gate: dict
    comparison: dict | None


class EvaluationDashboardResponse(BaseModel):
    latest: EvaluationRunResponse
    comparison: EvaluationComparisonResponse | None


class EvaluationRunStartResponse(BaseModel):
    evaluation_run_id: int
    status: str


class EvaluationHealthResponse(BaseModel):
    healthy: bool
    running_count: int
    stale_count: int
    cancelled_count: int


class StaleEvaluationRunResponse(BaseModel):
    id: int
    dataset_name: str
    status: str
    started_at: datetime
    duration_seconds: float


class StaleEvaluationRunsResponse(BaseModel):
    runs: list[StaleEvaluationRunResponse]


class EvaluationObservabilityResponse(BaseModel):
    event: str
    dataset: str
    total_cases: int
    retrieval_hit_rate: float
    average_groundedness: float
    average_semantic_relevance: float
    average_source_count: float
    overall_pass_rate: float
    quality_gate_passed: bool
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None
