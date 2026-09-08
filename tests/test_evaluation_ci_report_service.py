from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_ci_report_service import (
    build_evaluation_ci_report_for_repository,
)


def test_build_ci_report_when_deployment_is_ready():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=True,
    )

    repository.get_latest_run.return_value = latest_run

    readiness = Mock(
        ready=True,
        status="ready",
        reason="Evaluation quality checks passed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_ci_report_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ) as mock_build_readiness:
        result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "passed"
    assert result.quality_gate_passed is True
    assert result.deployment_ready is True
    assert result.message == ("Evaluation passed and deployment is allowed.")

    mock_build_readiness.assert_called_once_with(repository)


def test_build_ci_report_when_quality_gate_fails():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=False,
    )

    repository.get_latest_run.return_value = latest_run

    readiness = Mock(
        ready=False,
        status="blocked",
        reason="The evaluation quality gate failed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_ci_report_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ):
        result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "failed"
    assert result.quality_gate_passed is False
    assert result.deployment_ready is False
    assert result.message == ("Evaluation quality gate failed.")


def test_build_ci_report_when_no_evaluation_exists():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "failed"
    assert result.quality_gate_passed is False
    assert result.deployment_ready is False
