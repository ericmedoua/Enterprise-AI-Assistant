from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCIReport:
    status: str
    quality_gate_passed: bool
    deployment_ready: bool
    message: str
    retrieval_hit_rate: float
    average_groundedness: float
    average_semantic_relevance: float
    overall_pass_rate: float


def build_evaluation_ci_report(
    quality_gate_passed: bool,
    deployment_ready: bool,
    retrieval_hit_rate: float,
    average_groundedness: float,
    average_semantic_relevance: float,
    overall_pass_rate: float,
) -> EvaluationCIReport:
    if deployment_ready:
        return EvaluationCIReport(
            status="passed",
            quality_gate_passed=True,
            deployment_ready=True,
            message="Evaluation passed and deployment is allowed.",
            retrieval_hit_rate=retrieval_hit_rate,
            average_groundedness=average_groundedness,
            average_semantic_relevance=average_semantic_relevance,
            overall_pass_rate=overall_pass_rate,
        )

    if not quality_gate_passed:
        return EvaluationCIReport(
            status="failed",
            quality_gate_passed=False,
            deployment_ready=False,
            message="Evaluation quality gate failed.",
            retrieval_hit_rate=retrieval_hit_rate,
            average_groundedness=average_groundedness,
            average_semantic_relevance=average_semantic_relevance,
            overall_pass_rate=overall_pass_rate,
        )

    return EvaluationCIReport(
        status="failed",
        quality_gate_passed=True,
        deployment_ready=False,
        message=("Evaluation passed the quality gate but deployment is blocked."),
        retrieval_hit_rate=retrieval_hit_rate,
        average_groundedness=average_groundedness,
        average_semantic_relevance=average_semantic_relevance,
        overall_pass_rate=overall_pass_rate,
    )
