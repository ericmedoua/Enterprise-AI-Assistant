from app.ai.evaluation.experiment_gate import (
    ExperimentGateResult,
)

from app.ai.evaluation.experiment_gate_report import (
    format_experiment_gate_result,
)


def test_format_experiment_gate_pass():
    result = ExperimentGateResult(
        passed=True,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_pass_rate_passed=True,
    )

    output = format_experiment_gate_result(result)

    assert "Retrieval:          PASS" in output
    assert "DECISION: ACCEPT" in output


def test_format_experiment_gate_reject():
    result = ExperimentGateResult(
        passed=False,
        retrieval_passed=True,
        groundedness_passed=False,
        semantic_relevance_passed=True,
        overall_pass_rate_passed=False,
    )

    output = format_experiment_gate_result(result)

    assert "Groundedness:       FAIL" in output
    assert "DECISION: REJECT" in output
