from datetime import datetime

from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
    compare_evaluation_runs,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.ai.evaluation.evaluation_duration import (
    calculate_duration_seconds,
)
from app.models.evaluation_run import EvaluationRun
from app.schemas.evaluation import (
    EvaluationHistoryPagination,
    EvaluationHistoryResponse,
    EvaluationRunResponse,
)

from app.repositories.evaluation_history_filters import (
    EvaluationHistoryFilters,
    EvaluationHistoryQuery,
    EvaluationHistorySortField,
    EvaluationHistorySortOrder,
    EvaluationStatus,
)


def compare_latest_runs(
    repository: EvaluationRepository,
) -> EvaluationComparison | None:
    """
    Compare the two most recent evaluation runs.

    Returns None when fewer than two runs exist.
    """

    current = repository.get_latest_run()

    if current is None:
        return None

    previous = repository.get_previous_run(current.id)

    if previous is None:
        return None

    return compare_evaluation_runs(
        previous=previous,
        current=current,
    )


def get_evaluation_history(
    repository: EvaluationRepository,
    *,
    dataset_name: str | None = None,
    llm_model: str | None = None,
    embedding_model: str | None = None,
    status: EvaluationStatus | None = None,
    quality_gate_passed: bool | None = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    limit: int | None = None,
    offset: int = 0,
    sort_by: EvaluationHistorySortField = "created_at",
    sort_order: EvaluationHistorySortOrder = "desc",
) -> EvaluationHistoryResponse:
    history_filters = EvaluationHistoryFilters(
        dataset_name=dataset_name,
        llm_model=llm_model,
        embedding_model=embedding_model,
        status=status,
        quality_gate_passed=quality_gate_passed,
        created_after=created_after,
        created_before=created_before,
    )

    history_query = EvaluationHistoryQuery(
        filters=history_filters,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total = repository.count_runs(
        query=history_query,
    )

    runs = repository.list_runs(
        query=history_query,
    )

    return build_evaluation_history(
        runs,
        limit=limit,
        offset=offset,
        total=total,
    )


def build_evaluation_history(
    runs: list[EvaluationRun],
    *,
    limit: int | None = None,
    offset: int = 0,
    total: int | None = None,
) -> EvaluationHistoryResponse:
    responses = [
        EvaluationRunResponse(
            id=run.id,
            created_at=run.created_at,
            dataset_name=run.dataset_name,
            llm_model=run.llm_model,
            embedding_model=run.embedding_model,
            git_commit=run.git_commit,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            duration_seconds=calculate_duration_seconds(
                run.started_at,
                run.completed_at,
            ),
            total_cases=run.total_cases,
            retrieval_hit_rate=run.retrieval_hit_rate,
            average_groundedness=run.average_groundedness,
            average_semantic_relevance=(run.average_semantic_relevance),
            average_source_count=run.average_source_count,
            overall_pass_rate=run.overall_pass_rate,
            quality_gate_passed=run.quality_gate_passed,
        )
        for run in runs
    ]

    pagination = None

    if limit is not None and total is not None:
        pagination = EvaluationHistoryPagination(
            limit=limit,
            offset=offset,
            total=total,
            has_next=offset + len(responses) < total,
            has_previous=offset > 0,
        )

    return EvaluationHistoryResponse(
        runs=responses,
        pagination=pagination,
    )
