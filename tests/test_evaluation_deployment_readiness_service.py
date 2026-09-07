from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_deployment_readiness_service import (
    build_evaluation_deployment_readiness,
)


def test_build_deployment_readiness_when_quality_gate_passes():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=True,
    )

    repository.get_latest_run.return_value = latest_run

    trends = [Mock()]

    with (
        patch(
            "app.ai.evaluation.evaluation_deployment_readiness_service."
            "build_latest_evaluation_trends",
            return_value=trends,
        ),
        patch(
            "app.ai.evaluation.evaluation_deployment_readiness_service."
            "detect_evaluation_regressions",
            return_value=[],
        ),
    ):
        result = build_evaluation_deployment_readiness(repository)

    assert result.ready is True
    assert result.status == "ready"
    assert result.reason == "Evaluation quality checks passed."


def test_build_deployment_readiness_when_regression_exists():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=True,
    )

    repository.get_latest_run.return_value = latest_run

    trends = [Mock()]
    regressions = [Mock()]

    with (
        patch(
            "app.ai.evaluation.evaluation_deployment_readiness_service."
            "build_latest_evaluation_trends",
            return_value=trends,
        ),
        patch(
            "app.ai.evaluation.evaluation_deployment_readiness_service."
            "detect_evaluation_regressions",
            return_value=regressions,
        ),
    ):
        result = build_evaluation_deployment_readiness(repository)

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "Evaluation regressions were detected."


def test_build_deployment_readiness_when_quality_gate_fails():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=False,
    )

    repository.get_latest_run.return_value = latest_run

    trends = [Mock()]

    with (
        patch(
            "app.ai.evaluation.evaluation_deployment_readiness_service."
            "build_latest_evaluation_trends",
            return_value=trends,
        ),
        patch(
            "app.ai.evaluation.evaluation_deployment_readiness_service."
            "detect_evaluation_regressions",
            return_value=[],
        ),
    ):
        result = build_evaluation_deployment_readiness(repository)

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "The evaluation quality gate failed."


def test_build_deployment_readiness_when_no_evaluation_exists():
    repository = Mock()
    repository.get_latest_run.return_value = None

    result = build_evaluation_deployment_readiness(repository)

    assert result.ready is False
    assert result.status == "blocked"
    assert result.reason == "No evaluation run is available."
