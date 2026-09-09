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
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.95,
    )

    result = format_evaluation_ci_report(report)

    assert "RAG EVALUATION CI REPORT" in result
    assert "Status: PASSED" in result
    assert "Quality gate: PASSED" in result
    assert "Deployment: ALLOWED" in result
    assert "Reason: Evaluation passed and deployment is allowed." in result

    assert "Retrieval hit rate: 100.00%" in result
    assert "Groundedness: 90.00%" in result
    assert "Semantic relevance: 80.00%" in result
    assert "Overall pass rate: 95.00%" in result


def test_format_evaluation_ci_report_when_blocked():
    report = EvaluationCIReport(
        status="failed",
        quality_gate_passed=False,
        deployment_ready=False,
        message="Evaluation quality gate failed.",
        retrieval_hit_rate=0.8,
        average_groundedness=0.7,
        average_semantic_relevance=0.6,
        overall_pass_rate=0.5,
    )

    result = format_evaluation_ci_report(report)

    assert "Status: FAILED" in result
    assert "Quality gate: FAILED" in result
    assert "Deployment: BLOCKED" in result
    assert "Reason: Evaluation quality gate failed." in result

    assert "Retrieval hit rate: 80.00%" in result
    assert "Groundedness: 70.00%" in result
    assert "Semantic relevance: 60.00%" in result
    assert "Overall pass rate: 50.00%" in result


def test_format_evaluation_ci_report_when_quality_gate_passes_but_deployment_is_blocked():
    report = EvaluationCIReport(
        status="failed",
        quality_gate_passed=True,
        deployment_ready=False,
        message=("Evaluation passed the quality gate but deployment is blocked."),
        retrieval_hit_rate=0.8,
        average_groundedness=0.7,
        average_semantic_relevance=0.6,
        overall_pass_rate=0.5,
    )

    result = format_evaluation_ci_report(report)

    assert "Status: FAILED" in result
    assert "Quality gate: PASSED" in result
    assert "Deployment: BLOCKED" in result
    assert "Evaluation passed the quality gate but deployment is blocked." in result

    assert "Retrieval hit rate: 80.00%" in result
    assert "Groundedness: 70.00%" in result
    assert "Semantic relevance: 60.00%" in result
    assert "Overall pass rate: 50.00%" in result
