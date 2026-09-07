from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationDeploymentReadiness:
    ready: bool
    status: str
    reason: str


def evaluate_deployment_readiness(
    quality_gate_passed: bool,
    regression_count: int,
) -> EvaluationDeploymentReadiness:
    if not quality_gate_passed:
        return EvaluationDeploymentReadiness(
            ready=False,
            status="blocked",
            reason="The evaluation quality gate failed.",
        )

    if regression_count > 0:
        return EvaluationDeploymentReadiness(
            ready=False,
            status="blocked",
            reason="Evaluation regressions were detected.",
        )

    return EvaluationDeploymentReadiness(
        ready=True,
        status="ready",
        reason="Evaluation quality checks passed.",
    )
