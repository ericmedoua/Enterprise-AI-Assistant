import pytest

from app.ai.evaluation.evaluation_deployment_readiness import (
    evaluate_deployment_readiness,
)

from app.ai.evaluation.evaluation_deployment_readiness import (
    evaluate_deployment_readiness,
)


def test_deployment_is_ready_when_quality_gate_passes_and_no_regressions():
    result = evaluate_deployment_readiness(
        quality_gate_passed=True,
        regression_count=0,
    )

    assert result.ready is True
    assert result.status == "ready"
    assert result.reason == "Evaluation quality checks passed."


def test_deployment_is_blocked_when_quality_gate_fails():
    result = evaluate_deployment_readiness(
        quality_gate_passed=False,
        regression_count=0,
    )

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "The evaluation quality gate failed."


def test_deployment_is_blocked_when_regressions_exist():
    result = evaluate_deployment_readiness(
        quality_gate_passed=True,
        regression_count=1,
    )

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "Evaluation regressions were detected."


def test_deployment_is_blocked_when_quality_gate_fails_and_regressions_exist():
    result = evaluate_deployment_readiness(
        quality_gate_passed=False,
        regression_count=2,
    )

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "The evaluation quality gate failed."


@pytest.mark.parametrize(
    "quality_gate_passed,regression_count,expected_ready,expected_status",
    [
        (True, 0, True, "ready"),
        (False, 0, False, "blocked"),
        (True, 1, False, "blocked"),
        (False, 2, False, "blocked"),
    ],
)
def test_deployment_readiness_decision_matrix(
    quality_gate_passed,
    regression_count,
    expected_ready,
    expected_status,
):
    result = evaluate_deployment_readiness(
        quality_gate_passed=quality_gate_passed,
        regression_count=regression_count,
    )

    assert result.ready is expected_ready
    assert result.status == expected_status


def test_deployment_is_blocked_with_multiple_regressions():
    result = evaluate_deployment_readiness(
        quality_gate_passed=True,
        regression_count=5,
    )

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "Evaluation regressions were detected."
