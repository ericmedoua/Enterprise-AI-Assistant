from pathlib import Path

from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
)
from app.ai.evaluation.evaluation_ci_report_artifact import (
    write_evaluation_ci_report,
)
from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)


def test_write_evaluation_ci_report(tmp_path):
    report = EvaluationCIReport(
        status="failed",
        quality_gate_passed=False,
        deployment_ready=False,
        message="Evaluation quality gate failed.",
        retrieval_hit_rate=0.8,
        average_groundedness=0.7,
        average_semantic_relevance=0.6,
        overall_pass_rate=0.5,
        comparison=EvaluationComparison(
            retrieval_hit_rate_delta=0.1,
            groundedness_delta=-0.05,
            semantic_relevance_delta=0.02,
            source_count_delta=0.5,
            overall_pass_rate_delta=-0.10,
        ),
    )

    output_path = tmp_path / "evaluation-report.txt"

    result = write_evaluation_ci_report(
        report,
        output_path=str(output_path),
    )

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "RAG EVALUATION CI REPORT" in content
    assert "Status: FAILED" in content
    assert "Quality gate: FAILED" in content
    assert "Deployment: BLOCKED" in content
    assert "Evaluation quality gate failed." in content

    assert "EVALUATION COMPARISON" in content
    assert "Retrieval delta:         +10.00%" in content
    assert "Groundedness delta:      -5.00%" in content
    assert "Semantic relevance:      +2.00%" in content
    assert "Source count delta:      +0.50" in content
    assert "Overall pass-rate delta: -10.00%" in content


def test_write_evaluation_ci_report_creates_parent_directory(tmp_path):
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
            groundedness_delta=-0.05,
            semantic_relevance_delta=0.02,
            source_count_delta=0.5,
            overall_pass_rate_delta=-0.10,
        ),
    )

    output_path = tmp_path / "nested" / "reports" / "evaluation.txt"

    result = write_evaluation_ci_report(
        report,
        output_path=str(output_path),
    )

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")

    assert "RAG EVALUATION CI REPORT" in content
    assert "Status: PASSED" in content
    assert "Quality gate: PASSED" in content
    assert "Deployment: ALLOWED" in content

    assert "Retrieval hit rate: 100.00%" in content
    assert "Groundedness: 90.00%" in content
    assert "Semantic relevance: 80.00%" in content
    assert "Overall pass rate: 95.00%" in content

    assert "Evaluation passed and deployment is allowed." in content


def test_write_evaluation_ci_report_without_comparison(tmp_path):
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

    output_path = tmp_path / "evaluation-report.txt"

    result = write_evaluation_ci_report(
        report,
        output_path=str(output_path),
    )

    content = output_path.read_text(encoding="utf-8")

    assert result == output_path
    assert output_path.exists()
    assert "RAG EVALUATION CI REPORT" in content
    assert "Status: PASSED" in content
    assert "Deployment: ALLOWED" in content
    assert "Evaluation Metrics" in content
    assert "EVALUATION COMPARISON" not in content
