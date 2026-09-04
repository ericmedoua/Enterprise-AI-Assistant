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
    EvaluationHistoryResponse,
    EvaluationRunResponse,
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


def build_evaluation_history(
    runs: list[EvaluationRun],
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

    return EvaluationHistoryResponse(
        runs=responses,
    )
