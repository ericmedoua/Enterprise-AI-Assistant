from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
    EvaluationRegression,
)
from app.ai.evaluation.evaluation_ci_report_formatter import (
    format_evaluation_ci_report,
)
from app.ai.evaluation.evaluation_comparator import EvaluationComparison


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
        comparison=EvaluationComparison(
            retrieval_hit_rate_delta=0.1,
            groundedness_delta=0.05,
            semantic_relevance_delta=0.02,
            source_count_delta=0.5,
            overall_pass_rate_delta=0.05,
        ),
    )

    result = format_evaluation_ci_report(report)
    output = format_evaluation_ci_report(report, include_comparison=True)

    assert "RAG EVALUATION CI REPORT" in result
    assert "Status: PASSED" in result
    assert "Quality gate: PASSED" in result
    assert "Deployment: ALLOWED" in result
    assert "Reason: Evaluation passed and deployment is allowed." in result

    assert "Regression Details" not in result

    assert "Retrieval hit rate: 100.00%" in result
    assert "Groundedness: 90.00%" in result
    assert "Semantic relevance: 80.00%" in result
    assert "Overall pass rate: 95.00%" in result

    assert "EVALUATION COMPARISON" in output

    assert "Retrieval delta:         +10.00%" in output
    assert "Groundedness delta:      +5.00%" in output
    assert "Semantic relevance:      +2.00%" in output
    assert "Source count delta:      +0.50" in output
    assert "Overall pass-rate delta: +5.00%" in output


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


def test_format_evaluation_ci_report_without_comparison():
    report = EvaluationCIReport(
        status="passed",
        quality_gate_passed=True,
        deployment_ready=True,
        message="Evaluation passed and deployment is allowed.",
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.95,
        comparison=None,
    )

    result = format_evaluation_ci_report(
        report,
        include_comparison=True,
    )

    assert "RAG EVALUATION CI REPORT" in result
    assert "Evaluation Metrics" in result
    assert "EVALUATION COMPARISON" not in result
    assert "Reason: Evaluation passed and deployment is allowed." in result


def test_format_evaluation_ci_report_with_regressions():
    report = EvaluationCIReport(
        status="failed",
        quality_gate_passed=False,
        deployment_ready=False,
        message="Evaluation quality gate failed.",
        retrieval_hit_rate=1.0,
        average_groundedness=0.70,
        average_semantic_relevance=0.60,
        overall_pass_rate=0.50,
        regressions=[
            EvaluationRegression(
                metric_name="average_groundedness",
                previous_value=0.90,
                current_value=0.70,
                delta=-0.20,
                severity="critical",
            ),
            EvaluationRegression(
                metric_name="average_semantic_relevance",
                previous_value=0.80,
                current_value=0.60,
                delta=-0.20,
                severity="critical",
            ),
            EvaluationRegression(
                metric_name="overall_pass_rate",
                previous_value=1.00,
                current_value=0.50,
                delta=-0.50,
                severity="critical",
            ),
        ],
    )

    result = format_evaluation_ci_report(
        report,
        include_comparison=True,
    )

    assert "Regression Details" in result
    assert "- average_groundedness: -20.00% (critical)" in result
    assert "- average_semantic_relevance: -20.00% (critical)" in result
    assert "- overall_pass_rate: -50.00% (critical)" in result
