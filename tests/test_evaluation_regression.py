import pytest

from app.ai.evaluation.evaluation_regression import (
    classify_regression_severity,
    detect_evaluation_regressions,
    detect_metric_regression,
    is_metric_regression,
)
from app.ai.evaluation.evaluation_trends import EvaluationMetricTrend


def make_trend(
    previous_value: float,
    current_value: float,
    metric_name: str = "average_groundedness",
):
    return EvaluationMetricTrend(
        metric_name=metric_name,
        previous_value=previous_value,
        current_value=current_value,
        delta=current_value - previous_value,
        direction=(
            "improving"
            if current_value > previous_value
            else "declining"
            if current_value < previous_value
            else "stable"
        ),
    )


def test_is_metric_regression_for_declining_metric():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.80,
    )

    assert is_metric_regression(trend) is True


def test_is_metric_regression_for_small_decline():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.87,
    )

    assert is_metric_regression(trend) is False


def test_is_metric_regression_for_improving_metric():
    trend = make_trend(
        previous_value=0.80,
        current_value=0.90,
    )

    assert is_metric_regression(trend) is False


def test_classify_regression_severity_warning():
    assert classify_regression_severity(-0.05) == "warning"


def test_classify_regression_severity_critical():
    assert classify_regression_severity(-0.20) == "critical"


def test_classify_regression_severity_none():
    assert classify_regression_severity(-0.01) == "none"


def test_detect_metric_regression():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.80,
        metric_name="average_groundedness",
    )

    regression = detect_metric_regression(trend)

    assert regression is not None
    assert regression.metric_name == "average_groundedness"
    assert regression.previous_value == 0.90
    assert regression.current_value == 0.80
    assert regression.delta == pytest.approx(-0.10)
    assert regression.severity == "warning"


def test_detect_metric_regression_returns_none_for_non_regression():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.88,
    )

    regression = detect_metric_regression(trend)

    assert regression is None


def test_detect_evaluation_regressions_returns_only_regressions():
    trends = [
        make_trend(
            previous_value=0.90,
            current_value=0.80,
            metric_name="average_groundedness",
        ),
        make_trend(
            previous_value=0.60,
            current_value=0.61,
            metric_name="average_semantic_relevance",
        ),
        make_trend(
            previous_value=0.50,
            current_value=0.20,
            metric_name="overall_pass_rate",
        ),
    ]

    regressions = detect_evaluation_regressions(trends)

    assert len(regressions) == 2

    assert regressions[0].metric_name == "average_groundedness"
    assert regressions[0].severity == "warning"

    assert regressions[1].metric_name == "overall_pass_rate"
    assert regressions[1].severity == "critical"


def test_detect_evaluation_regressions_with_no_trends():
    regressions = detect_evaluation_regressions([])

    assert regressions == []


def test_regression_threshold_boundary_is_not_regression():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.85,
    )

    assert trend.delta == pytest.approx(-0.05)
    assert is_metric_regression(trend) is False


def test_regression_just_below_threshold_is_warning():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.849,
    )

    assert trend.delta == pytest.approx(-0.051)
    assert is_metric_regression(trend) is True

    regression = detect_metric_regression(trend)

    assert regression is not None
    assert regression.severity == "warning"


def test_large_regression_is_critical():
    trend = make_trend(
        previous_value=0.90,
        current_value=0.69,
    )

    assert trend.delta == pytest.approx(-0.21)

    regression = detect_metric_regression(trend)

    assert regression is not None
    assert regression.severity == "critical"
