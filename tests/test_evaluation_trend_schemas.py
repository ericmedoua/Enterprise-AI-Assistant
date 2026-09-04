from app.schemas.evaluation import (
    EvaluationMetricTrendResponse,
    EvaluationTrendResponse,
)


def test_evaluation_metric_trend_response():
    result = EvaluationMetricTrendResponse(
        metric_name="retrieval_hit_rate",
        previous_value=0.8,
        current_value=1.0,
        delta=0.2,
        direction="improving",
    )

    assert result.metric_name == "retrieval_hit_rate"
    assert result.previous_value == 0.8
    assert result.current_value == 1.0
    assert result.delta == 0.2
    assert result.direction == "improving"


def test_evaluation_trend_response():
    result = EvaluationTrendResponse(
        trends=[
            EvaluationMetricTrendResponse(
                metric_name="retrieval_hit_rate",
                previous_value=0.8,
                current_value=1.0,
                delta=0.2,
                direction="improving",
            )
        ]
    )

    assert len(result.trends) == 1
    assert result.trends[0].metric_name == "retrieval_hit_rate"
