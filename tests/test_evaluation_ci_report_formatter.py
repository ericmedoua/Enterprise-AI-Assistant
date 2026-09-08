from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
)
from app.ai.evaluation.evaluation_ci_report_formatter import (
    format_evaluation_ci_report,
)


def test_format_evaluation_ci_report_when_passed():
    report = EvaluationCIReport(
        status="passed",
        quality_gate_passed=True,
        deployment_ready=True,
        message="Evaluation passed and deployment is allowed.",
    )

    result = format_evaluation_ci_report(report)

    assert "RAG EVALUATION CI REPORT" in result
    assert "Status: PASSED" in result
    assert "Quality gate: PASSED" in result
    assert "Deployment: ALLOWED" in result
    assert "Reason: Evaluation passed and deployment is allowed." in result


def test_format_evaluation_ci_report_when_blocked():
    report = EvaluationCIReport(
        status="failed",
        quality_gate_passed=False,
        deployment_ready=False,
        message="Evaluation quality gate failed.",
    )

    result = format_evaluation_ci_report(report)

    assert "Status: FAILED" in result
    assert "Quality gate: FAILED" in result
    assert "Deployment: BLOCKED" in result
    assert "Reason: Evaluation quality gate failed." in result


def test_format_evaluation_ci_report_when_quality_gate_passes_but_deployment_is_blocked():
    report = EvaluationCIReport(
        status="failed",
        quality_gate_passed=True,
        deployment_ready=False,
        message=("Evaluation passed the quality gate but deployment is blocked."),
    )

    result = format_evaluation_ci_report(report)

    assert "Status: FAILED" in result
    assert "Quality gate: PASSED" in result
    assert "Deployment: BLOCKED" in result
    assert "Evaluation passed the quality gate but deployment is blocked." in result
