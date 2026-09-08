from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
    build_evaluation_ci_report,
)
from app.ai.evaluation.evaluation_deployment_readiness_service import (
    build_evaluation_deployment_readiness,
)


def build_evaluation_ci_report_for_repository(
    repository,
) -> EvaluationCIReport:
    latest_run = repository.get_latest_run()

    if latest_run is None:
        return build_evaluation_ci_report(
            quality_gate_passed=False,
            deployment_ready=False,
        )

    readiness = build_evaluation_deployment_readiness(repository)

    return build_evaluation_ci_report(
        quality_gate_passed=latest_run.quality_gate_passed,
        deployment_ready=readiness.ready,
    )
