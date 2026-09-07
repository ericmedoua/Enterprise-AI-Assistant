from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationDeploymentGate:
    allowed: bool
    exit_code: int
    message: str


def evaluate_deployment_gate(
    ready: bool,
) -> EvaluationDeploymentGate:
    if ready:
        return EvaluationDeploymentGate(
            allowed=True,
            exit_code=0,
            message="Deployment allowed: evaluation checks passed.",
        )

    return EvaluationDeploymentGate(
        allowed=False,
        exit_code=1,
        message="Deployment blocked: evaluation checks failed.",
    )
