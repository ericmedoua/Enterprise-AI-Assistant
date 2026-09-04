from app.ai.evaluation.evaluation_quality_health import (
    EvaluationQualityHealth,
)


def test_evaluation_quality_health_can_be_created():
    result = EvaluationQualityHealth(
        healthy=True,
        status="healthy",
        latest_run_id=100,
        quality_gate_passed=True,
        trend_status="stable",
    )

    assert result.healthy is True
    assert result.status == "healthy"
    assert result.latest_run_id == 100
    assert result.quality_gate_passed is True
    assert result.trend_status == "stable"
