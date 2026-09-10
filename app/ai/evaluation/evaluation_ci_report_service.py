from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
    build_evaluation_ci_report,
)
from app.ai.evaluation.evaluation_deployment_readiness_service import (
    build_evaluation_deployment_readiness,
)
from app.ai.evaluation.evaluation_comparator import compare_evaluation_runs


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

    comparison = None

    previous_run = repository.get_previous_run(latest_run.id)

    comparison = (
        compare_evaluation_runs(
            previous=previous_run,
            current=latest_run,
        )
        if previous_run is not None
        else None
    )

    readiness = build_evaluation_deployment_readiness(repository)

    return build_evaluation_ci_report(
        quality_gate_passed=latest_run.quality_gate_passed,
        deployment_ready=readiness.ready,
        retrieval_hit_rate=latest_run.retrieval_hit_rate,
        average_groundedness=latest_run.average_groundedness,
        average_semantic_relevance=latest_run.average_semantic_relevance,
        overall_pass_rate=latest_run.overall_pass_rate,
        comparison=comparison,
    )
