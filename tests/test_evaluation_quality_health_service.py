from unittest.mock import Mock, patch
from app.ai.evaluation.evaluation_quality_health_service import (
    build_evaluation_quality_health,
)


def make_run(
    run_id: int,
    quality_gate_passed: bool = True,
):
    run = Mock()

    run.id = run_id
    run.quality_gate_passed = quality_gate_passed

    return run


def make_trend(direction: str):
    trend = Mock()
    trend.direction = direction
    return trend


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_quality_health_healthy_with_stable_trends(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    mock_build_trends.return_value = [
        make_trend("stable"),
        make_trend("stable"),
        make_trend("stable"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is True
    assert result.status == "healthy"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "stable"

    repository.get_latest_run.assert_called_once()

    mock_build_trends.assert_called_once_with(repository)


def test_quality_health_no_latest_run():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = build_evaluation_quality_health(repository)

    assert result.healthy is False
    assert result.status == "unhealthy"
    assert result.latest_run_id is None
    assert result.quality_gate_passed is False
    assert result.trend_status == "stable"

    repository.get_latest_run.assert_called_once()


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_quality_health_quality_gate_failed(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=False,
    )

    mock_build_trends.return_value = [
        make_trend("stable"),
        make_trend("stable"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is False
    assert result.status == "degraded"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is False
    assert result.trend_status == "stable"

    repository.get_latest_run.assert_called_once()

    mock_build_trends.assert_called_once_with(repository)


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_overall_declining_metric_degrades_health(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    mock_build_trends.return_value = [
        make_trend("stable"),
        make_trend("declining"),
        make_trend("stable"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is False
    assert result.status == "degraded"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "declining"

    repository.get_latest_run.assert_called_once()
    mock_build_trends.assert_called_once_with(repository)


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_overall_improving_metric_is_healthy(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    mock_build_trends.return_value = [
        make_trend("stable"),
        make_trend("improving"),
        make_trend("stable"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is True
    assert result.status == "healthy"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "improving"


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_quality_health_mixed_trends_with_declining_metric(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    mock_build_trends.return_value = [
        make_trend("improving"),
        make_trend("stable"),
        make_trend("declining"),
        make_trend("improving"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is False
    assert result.status == "degraded"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "declining"


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_quality_health_all_stable(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    mock_build_trends.return_value = [
        make_trend("stable"),
        make_trend("stable"),
        make_trend("stable"),
        make_trend("stable"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is True
    assert result.status == "healthy"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "stable"


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_quality_health_without_enough_history(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    mock_build_trends.return_value = []

    result = build_evaluation_quality_health(repository)

    assert result.healthy is True
    assert result.status == "healthy"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "stable"


@patch(
    "app.ai.evaluation.evaluation_quality_health_service.build_latest_evaluation_trends"
)
def test_quality_health_quality_gate_failure_with_improving_trend(
    mock_build_trends,
):
    repository = Mock()

    repository.get_latest_run.return_value = make_run(
        run_id=100,
        quality_gate_passed=False,
    )

    mock_build_trends.return_value = [
        make_trend("improving"),
        make_trend("improving"),
    ]

    result = build_evaluation_quality_health(repository)

    assert result.healthy is False
    assert result.status == "degraded"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is False
    assert result.trend_status == "improving"
