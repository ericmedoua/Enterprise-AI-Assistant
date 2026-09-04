import pytest
from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_dashboard_service import (
    EvaluationDashboard,
    build_evaluation_dashboard,
)


@patch("app.ai.evaluation.evaluation_dashboard_service.evaluate_health")
@patch("app.ai.evaluation.evaluation_dashboard_service.build_evaluation_quality_health")
@patch("app.ai.evaluation.evaluation_dashboard_service.compare_evaluation_runs")
def test_build_evaluation_dashboard(
    mock_compare,
    mock_quality_health,
    mock_evaluate_health,
):
    repository = Mock()

    latest = Mock(id=10)
    previous = Mock(id=9)

    repository.get_latest_run.return_value = latest
    repository.get_previous_run.return_value = previous
    repository.list_running_runs.return_value = []
    repository.count_cancelled_runs.return_value = 0

    comparison = Mock()
    quality_health = Mock()
    operational_health = Mock()

    mock_compare.return_value = comparison
    mock_quality_health.return_value = quality_health
    mock_evaluate_health.return_value = operational_health

    result = build_evaluation_dashboard(repository)

    assert isinstance(result, EvaluationDashboard)

    assert result.latest is latest
    assert result.comparison is comparison
    assert result.quality_health is quality_health
    assert result.operational_health is operational_health

    repository.get_latest_run.assert_called_once()

    repository.get_previous_run.assert_called_once_with(10)

    repository.list_running_runs.assert_called_once()

    repository.count_cancelled_runs.assert_called_once()

    mock_compare.assert_called_once_with(
        previous=previous,
        current=latest,
    )

    mock_quality_health.assert_called_once_with(repository)

    mock_evaluate_health.assert_called_once_with(
        [],
        cancelled_count=0,
    )


def test_build_evaluation_dashboard_without_latest_run():
    repository = Mock()

    repository.get_latest_run.return_value = None

    with pytest.raises(
        ValueError,
        match="No evaluation runs found.",
    ):
        build_evaluation_dashboard(repository)

    repository.get_previous_run.assert_not_called()
    repository.list_running_runs.assert_not_called()
    repository.count_cancelled_runs.assert_not_called()


@patch("app.ai.evaluation.evaluation_dashboard_service.evaluate_health")
@patch("app.ai.evaluation.evaluation_dashboard_service.build_evaluation_quality_health")
def test_build_evaluation_dashboard_without_previous_run(
    mock_quality_health,
    mock_evaluate_health,
):
    repository = Mock()

    latest = Mock(id=10)

    repository.get_latest_run.return_value = latest
    repository.get_previous_run.return_value = None
    repository.list_running_runs.return_value = []
    repository.count_cancelled_runs.return_value = 0

    quality_health = Mock()
    operational_health = Mock()

    mock_quality_health.return_value = quality_health
    mock_evaluate_health.return_value = operational_health

    result = build_evaluation_dashboard(repository)

    assert result.latest is latest
    assert result.comparison is None
    assert result.quality_health is quality_health
    assert result.operational_health is operational_health

    repository.get_previous_run.assert_called_once_with(10)
