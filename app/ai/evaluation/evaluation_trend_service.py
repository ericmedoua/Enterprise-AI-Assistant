from app.ai.evaluation.evaluation_trends import (
    EvaluationMetricTrend,
    build_evaluation_trends,
)
from app.repositories.evaluation_repository import EvaluationRepository


def build_latest_evaluation_trends(
    repository: EvaluationRepository,
) -> list[EvaluationMetricTrend]:
    runs = repository.list_runs()

    if len(runs) < 2:
        return []

    current = runs[0]
    previous = runs[1]

    return build_evaluation_trends(
        previous=previous,
        current=current,
    )
