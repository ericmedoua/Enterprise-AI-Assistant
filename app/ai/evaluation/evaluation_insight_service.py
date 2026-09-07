from app.ai.evaluation.evaluation_insights import (
    EvaluationInsight,
    build_evaluation_insights,
)
from app.ai.evaluation.evaluation_trend_service import (
    build_latest_evaluation_trends,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.ai.evaluation.evaluation_regression import (
    detect_evaluation_regressions,
)


def build_latest_evaluation_insights(
    repository: EvaluationRepository,
) -> list[EvaluationInsight]:
    latest_run = repository.get_latest_run()

    if latest_run is None:
        return []

    trends = build_latest_evaluation_trends(repository)

    regressions = detect_evaluation_regressions(trends)

    return build_evaluation_insights(
        quality_gate_passed=latest_run.quality_gate_passed,
        trends=trends,
        regressions=regressions,
    )
