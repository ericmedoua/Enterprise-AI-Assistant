import pytest

from app.ai.evaluation.evaluation_trends import (
    calculate_trend_direction,
    calculate_metric_trend,
)


def test_calculate_trend_direction_improving():
    result = calculate_trend_direction(0.80, 0.90)

    assert result == "improving"


def test_calculate_trend_direction_declining():
    result = calculate_trend_direction(0.90, 0.80)

    assert result == "declining"


def test_calculate_trend_direction_stable():
    result = calculate_trend_direction(0.80, 0.8005)

    assert result == "stable"


def test_calculate_metric_trend():
    result = calculate_metric_trend(
        metric_name="retrieval_hit_rate",
        previous_value=0.80,
        current_value=0.90,
    )

    assert result.metric_name == "retrieval_hit_rate"
    assert result.previous_value == 0.80
    assert result.current_value == 0.90
    assert result.delta == pytest.approx(0.10)
    assert result.direction == "improving"
