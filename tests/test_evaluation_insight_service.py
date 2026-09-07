from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_insight_service import (
    build_latest_evaluation_insights,
)
from app.ai.evaluation.evaluation_regression import EvaluationRegression


def make_run(
    run_id: int,
    quality_gate_passed: bool = True,
):
    run = Mock()

    run.id = run_id
    run.quality_gate_passed = quality_gate_passed

    return run


def make_trend(
    metric_name: str,
    direction: str,
):
    trend = Mock()

    trend.metric_name = metric_name
    trend.direction = direction

    return trend


@patch("app.ai.evaluation.evaluation_insight_service.detect_evaluation_regressions")
@patch("app.ai.evaluation.evaluation_insight_service.build_latest_evaluation_trends")
@patch("app.ai.evaluation.evaluation_insight_service.build_evaluation_insights")
def test_build_latest_evaluation_insights(
    mock_build_insights,
    mock_build_trends,
    mock_detect_regressions,
):
    repository = Mock()

    latest = make_run(
        run_id=100,
        quality_gate_passed=True,
    )

    repository.get_latest_run.return_value = latest

    trends = [
        make_trend(
            "average_groundedness",
            "declining",
        )
    ]

    insights = [
        Mock(
            metric_name="average_groundedness",
            severity="warning",
        )
    ]

    mock_build_trends.return_value = trends
    mock_build_insights.return_value = insights
    mock_detect_regressions.return_value = []

    result = build_latest_evaluation_insights(repository)

    assert result is insights

    repository.get_latest_run.assert_called_once()

    mock_build_trends.assert_called_once_with(repository)

    mock_detect_regressions.assert_called_once_with(trends)

    mock_build_insights.assert_called_once_with(
        quality_gate_passed=True,
        trends=trends,
        regressions=[],
    )


def test_build_latest_evaluation_insights_without_latest_run():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = build_latest_evaluation_insights(repository)

    assert result == []

    repository.get_latest_run.assert_called_once()
    repository.list_runs.assert_not_called()


@patch("app.ai.evaluation.evaluation_insight_service.detect_evaluation_regressions")
@patch("app.ai.evaluation.evaluation_insight_service.build_latest_evaluation_trends")
@patch("app.ai.evaluation.evaluation_insight_service.build_evaluation_insights")
def test_build_latest_evaluation_insights_with_failed_quality_gate(
    mock_build_insights,
    mock_build_trends,
    mock_detect_regressions,
):
    repository = Mock()

    latest = make_run(
        run_id=101,
        quality_gate_passed=False,
    )

    repository.get_latest_run.return_value = latest

    trends = [
        make_trend(
            "average_groundedness",
            "stable",
        )
    ]

    mock_build_trends.return_value = trends
    mock_detect_regressions.return_value = []
    expected = [
        Mock(
            metric_name="average_groundedness",
            severity="warning",
        )
    ]
    mock_build_insights.return_value = expected

    result = build_latest_evaluation_insights(repository)

    assert result is expected

    mock_detect_regressions.assert_called_once_with(trends)

    mock_build_insights.assert_called_once_with(
        quality_gate_passed=False,
        trends=trends,
        regressions=[],
    )
