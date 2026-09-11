from dataclasses import dataclass
from app.ai.evaluation.evaluation_comparator import EvaluationComparison
from app.ai.evaluation.evaluation_regression import EvaluationRegression


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
    comparison: EvaluationComparison | None = None
    regressions: list[EvaluationRegression] | None = None


def build_evaluation_ci_report(
    quality_gate_passed: bool,
    deployment_ready: bool,
    retrieval_hit_rate: float,
    average_groundedness: float,
    average_semantic_relevance: float,
    overall_pass_rate: float,
    comparison: EvaluationComparison | None = None,
    regressions: list[EvaluationRegression] | None = None,
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
            comparison=comparison,
            regressions=regressions,
        )

    if not quality_gate_passed:
        message = (
            "Evaluation quality gate failed."
            if not regressions
            else (
                "Evaluation quality gate failed and "
                "evaluation regressions were detected."
            )
        )

        return EvaluationCIReport(
            status="failed",
            quality_gate_passed=False,
            deployment_ready=False,
            message=message,
            retrieval_hit_rate=retrieval_hit_rate,
            average_groundedness=average_groundedness,
            average_semantic_relevance=average_semantic_relevance,
            overall_pass_rate=overall_pass_rate,
            comparison=comparison,
            regressions=regressions,
        )

    message = (
        "Evaluation passed the quality gate but deployment is blocked."
        if not regressions
        else (
            "Evaluation passed the quality gate but "
            "deployment is blocked by evaluation regressions."
        )
    )

    return EvaluationCIReport(
        status="failed",
        quality_gate_passed=True,
        deployment_ready=False,
        message=message,
        retrieval_hit_rate=retrieval_hit_rate,
        average_groundedness=average_groundedness,
        average_semantic_relevance=average_semantic_relevance,
        overall_pass_rate=overall_pass_rate,
        comparison=comparison,
        regressions=regressions,
    )
