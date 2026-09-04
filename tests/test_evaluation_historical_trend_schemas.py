from datetime import datetime, timezone

from app.schemas.evaluation import (
    EvaluationHistoricalTrendResponse,
    EvaluationHistoricalTrendsResponse,
    EvaluationMetricPointResponse,
)


def test_evaluation_metric_point_response():
    created_at = datetime(
        2026,
        8,
        31,
        20,
        34,
        20,
        tzinfo=timezone.utc,
    )

    result = EvaluationMetricPointResponse(
        run_id=661,
        created_at=created_at,
        value=0.9,
    )

    assert result.run_id == 661
    assert result.created_at == created_at
    assert result.value == 0.9


def test_evaluation_historical_trend_response():
    created_at = datetime(
        2026,
        8,
        31,
        20,
        34,
        20,
        tzinfo=timezone.utc,
    )

    point = EvaluationMetricPointResponse(
        run_id=661,
        created_at=created_at,
        value=0.9,
    )

    result = EvaluationHistoricalTrendResponse(
        metric_name="retrieval_hit_rate",
        points=[point],
        direction="improving",
    )

    assert result.metric_name == "retrieval_hit_rate"
    assert len(result.points) == 1
    assert result.points[0].run_id == 661
    assert result.direction == "improving"


def test_evaluation_historical_trends_response():
    created_at = datetime(
        2026,
        8,
        31,
        20,
        34,
        20,
        tzinfo=timezone.utc,
    )

    point = EvaluationMetricPointResponse(
        run_id=661,
        created_at=created_at,
        value=0.9,
    )

    trend = EvaluationHistoricalTrendResponse(
        metric_name="retrieval_hit_rate",
        points=[point],
        direction="improving",
    )

    result = EvaluationHistoricalTrendsResponse(
        trends=[trend],
    )

    assert len(result.trends) == 1
    assert result.trends[0].metric_name == ("retrieval_hit_rate")
