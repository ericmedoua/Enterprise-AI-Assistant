from app.schemas.evaluation import (
    EvaluationQualityHealthResponse,
)


def test_evaluation_quality_health_response():
    result = EvaluationQualityHealthResponse(
        healthy=True,
        status="healthy",
        latest_run_id=100,
        quality_gate_passed=True,
        trend_status="improving",
    )

    assert result.healthy is True
    assert result.status == "healthy"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "improving"


def test_evaluation_quality_health_response_without_latest_run():
    result = EvaluationQualityHealthResponse(
        healthy=False,
        status="unhealthy",
        latest_run_id=None,
        quality_gate_passed=False,
        trend_status="stable",
    )

    assert result.healthy is False
    assert result.status == "unhealthy"
    assert result.latest_run_id is None
    assert result.quality_gate_passed is False
    assert result.trend_status == "stable"
