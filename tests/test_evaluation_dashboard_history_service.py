from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_dashboard_history_service import (
    build_evaluation_dashboard_history,
)


def test_build_evaluation_dashboard_history():
    latest = Mock(
        id=991,
        quality_gate_passed=True,
    )

    previous = Mock(
        id=981,
        quality_gate_passed=False,
    )

    repository = Mock()
    repository.list_runs.return_value = [
        latest,
        previous,
    ]

    trends = [Mock()]

    with patch(
        "app.ai.evaluation.evaluation_dashboard_history_service."
        "build_evaluation_historical_trends",
        return_value=trends,
    ):
        history = build_evaluation_dashboard_history(repository)

    assert history.total_runs == 2
    assert history.passed_runs == 1
    assert history.failed_runs == 1
    assert history.pass_rate == 0.5
    assert history.latest_run_id == 991
    assert history.latest_quality_gate_passed is True
    assert history.trends == trends

    repository.list_runs.assert_called_once_with(limit=None)


def test_build_evaluation_dashboard_history_with_limit():
    run = Mock(
        id=991,
        quality_gate_passed=True,
    )

    repository = Mock()
    repository.list_runs.return_value = [run]

    trends = [Mock()]

    with patch(
        "app.ai.evaluation.evaluation_dashboard_history_service."
        "build_evaluation_historical_trends",
        return_value=trends,
    ):
        history = build_evaluation_dashboard_history(
            repository,
            limit=10,
        )

    assert history.total_runs == 1
    assert history.passed_runs == 1
    assert history.failed_runs == 0
    assert history.pass_rate == 1.0
    assert history.latest_run_id == 991
    assert history.latest_quality_gate_passed is True

    repository.list_runs.assert_called_once_with(limit=10)


def test_build_evaluation_dashboard_history_with_no_runs():
    repository = Mock()
    repository.list_runs.return_value = []

    trends = [Mock()]

    with patch(
        "app.ai.evaluation.evaluation_dashboard_history_service."
        "build_evaluation_historical_trends",
        return_value=trends,
    ):
        history = build_evaluation_dashboard_history(repository)

    assert history.total_runs == 0
    assert history.passed_runs == 0
    assert history.failed_runs == 0
    assert history.pass_rate == 0.0
    assert history.latest_run_id is None
    assert history.latest_quality_gate_passed is None
    assert history.trends == trends
