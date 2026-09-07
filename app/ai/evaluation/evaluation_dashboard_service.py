from dataclasses import dataclass

from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
    compare_evaluation_runs,
)
from app.ai.evaluation.evaluation_health import (
    EvaluationHealth,
    evaluate_health,
)
from app.ai.evaluation.evaluation_quality_health import (
    EvaluationQualityHealth,
)
from app.ai.evaluation.evaluation_quality_health_service import (
    build_evaluation_quality_health,
)
from app.models.evaluation_run import EvaluationRun
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.ai.evaluation.evaluation_insights import (
    EvaluationInsight,
)
from app.ai.evaluation.evaluation_insight_service import (
    build_latest_evaluation_insights,
)
from app.ai.evaluation.evaluation_deployment_readiness import (
    EvaluationDeploymentReadiness,
)
from app.ai.evaluation.evaluation_deployment_readiness_service import (
    build_evaluation_deployment_readiness,
)


@dataclass(frozen=True)
class EvaluationDashboard:
    latest: EvaluationRun
    comparison: EvaluationComparison | None
    quality_health: EvaluationQualityHealth
    operational_health: EvaluationHealth
    insights: list[EvaluationInsight]
    deployment_readiness: EvaluationDeploymentReadiness


def build_evaluation_dashboard(
    repository: EvaluationRepository,
) -> EvaluationDashboard:
    latest = repository.get_latest_run()

    if latest is None:
        raise ValueError("No evaluation runs found.")

    previous = repository.get_previous_run(latest.id)

    comparison = None

    if previous is not None:
        comparison = compare_evaluation_runs(
            previous=previous,
            current=latest,
        )

    quality_health = build_evaluation_quality_health(repository)

    insights = build_latest_evaluation_insights(repository)

    running_runs = repository.list_running_runs()

    cancelled_count = repository.count_cancelled_runs()

    operational_health = evaluate_health(
        running_runs,
        cancelled_count=cancelled_count,
    )

    deployment_readiness = build_evaluation_deployment_readiness(repository)

    return EvaluationDashboard(
        latest=latest,
        comparison=comparison,
        quality_health=quality_health,
        operational_health=operational_health,
        insights=insights,
        deployment_readiness=deployment_readiness,
    )
