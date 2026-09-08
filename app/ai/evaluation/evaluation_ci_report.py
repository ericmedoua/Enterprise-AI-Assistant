from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCIReport:
    status: str
    quality_gate_passed: bool
    deployment_ready: bool
    message: str


def build_evaluation_ci_report(
    quality_gate_passed: bool,
    deployment_ready: bool,
) -> EvaluationCIReport:
    if deployment_ready:
        return EvaluationCIReport(
            status="passed",
            quality_gate_passed=True,
            deployment_ready=True,
            message="Evaluation passed and deployment is allowed.",
        )

    if not quality_gate_passed:
        return EvaluationCIReport(
            status="failed",
            quality_gate_passed=False,
            deployment_ready=False,
            message="Evaluation quality gate failed.",
        )

    return EvaluationCIReport(
        status="failed",
        quality_gate_passed=True,
        deployment_ready=False,
        message="Evaluation passed the quality gate but deployment is blocked.",
    )
