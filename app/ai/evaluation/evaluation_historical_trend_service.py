from app.ai.evaluation.evaluation_historical_trends import (
    EvaluationHistoricalTrend,
    build_historical_evaluation_trends,
)
from app.repositories.evaluation_repository import EvaluationRepository


def build_evaluation_historical_trends_from_runs(
    runs,
) -> list[EvaluationHistoricalTrend]:
    return build_historical_evaluation_trends(runs)


def build_evaluation_historical_trends(
    repository: EvaluationRepository,
    limit: int | None = None,
) -> list[EvaluationHistoricalTrend]:
    runs = repository.list_runs(
        limit=limit,
    )

    return build_evaluation_historical_trends_from_runs(runs)
