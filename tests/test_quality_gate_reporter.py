from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)

from app.ai.evaluation.quality_gate_reporter import (
    format_quality_gate_result,
)


def test_format_quality_gate_pass():
    result = QualityGateResult(
        passed=True,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=True,
    )

    output = format_quality_gate_result(result)

    assert "Retrieval:         PASS" in output
    assert "FINAL: PASS" in output


def test_format_quality_gate_failure():
    result = QualityGateResult(
        passed=False,
        retrieval_passed=True,
        groundedness_passed=False,
        semantic_relevance_passed=True,
        overall_passed=False,
    )

    output = format_quality_gate_result(result)

    assert "Groundedness:      FAIL" in output
    assert "FINAL: FAIL" in output
