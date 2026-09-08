from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
)


def format_evaluation_ci_report(
    report: EvaluationCIReport,
) -> str:
    quality_gate = "PASSED" if report.quality_gate_passed else "FAILED"

    deployment = "ALLOWED" if report.deployment_ready else "BLOCKED"

    return (
        "========================================\n"
        "RAG EVALUATION CI REPORT\n"
        "========================================\n"
        f"Status: {report.status.upper()}\n"
        f"Quality gate: {quality_gate}\n"
        f"Deployment: {deployment}\n"
        f"\nReason: {report.message}\n"
        "========================================"
    )
