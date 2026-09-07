from app.ai.evaluation.evaluation_deployment_readiness import (
    EvaluationDeploymentReadiness,
    evaluate_deployment_readiness,
)
from app.ai.evaluation.evaluation_regression import (
    detect_evaluation_regressions,
)
from app.ai.evaluation.evaluation_trend_service import (
    build_latest_evaluation_trends,
)


def build_evaluation_deployment_readiness(
    repository,
) -> EvaluationDeploymentReadiness:
    latest_run = repository.get_latest_run()

    if latest_run is None:
        return EvaluationDeploymentReadiness(
            ready=False,
            status="blocked",
            reason="No evaluation run is available.",
        )

    trends = build_latest_evaluation_trends(repository)

    regressions = detect_evaluation_regressions(trends)

    return evaluate_deployment_readiness(
        quality_gate_passed=latest_run.quality_gate_passed,
        regression_count=len(regressions),
    )
