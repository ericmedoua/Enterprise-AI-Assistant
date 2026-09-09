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
            retrieval_hit_rate=0.0,
            average_groundedness=0.0,
            average_semantic_relevance=0.0,
            overall_pass_rate=0.0,
        )

    readiness = build_evaluation_deployment_readiness(repository)

    return build_evaluation_ci_report(
        quality_gate_passed=latest_run.quality_gate_passed,
        deployment_ready=readiness.ready,
        retrieval_hit_rate=latest_run.retrieval_hit_rate,
        average_groundedness=latest_run.average_groundedness,
        average_semantic_relevance=latest_run.average_semantic_relevance,
        overall_pass_rate=latest_run.overall_pass_rate,
    )
