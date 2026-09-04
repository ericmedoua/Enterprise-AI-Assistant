from app.ai.evaluation.evaluation_quality_health import (
    EvaluationQualityHealth,
)
from app.ai.evaluation.evaluation_trend_service import (
    build_latest_evaluation_trends,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)
from types import SimpleNamespace
from unittest.mock import Mock, patch


def make_trend(direction):
    return SimpleNamespace(direction=direction)


def make_run(run_id, quality_gate_passed):
    return SimpleNamespace(id=run_id, quality_gate_passed=quality_gate_passed)


def _calculate_overall_trend_status(trends) -> str:
    if not trends:
        return "stable"

    if any(trend.direction == "declining" for trend in trends):
        return "declining"

    if any(trend.direction == "improving" for trend in trends):
        return "improving"

    return "stable"


def build_evaluation_quality_health(
    repository: EvaluationRepository,
) -> EvaluationQualityHealth:
    latest_run = repository.get_latest_run()

    if latest_run is None:
        return EvaluationQualityHealth(
            healthy=False,
            status="unhealthy",
            latest_run_id=None,
            quality_gate_passed=False,
            trend_status="stable",
        )

    trends = build_latest_evaluation_trends(repository)

    trend_status = _calculate_overall_trend_status(trends)

    if not latest_run.quality_gate_passed:
        return EvaluationQualityHealth(
            healthy=False,
            status="degraded",
            latest_run_id=latest_run.id,
            quality_gate_passed=False,
            trend_status=trend_status,
        )

    if trend_status == "declining":
        return EvaluationQualityHealth(
            healthy=False,
            status="degraded",
            latest_run_id=latest_run.id,
            quality_gate_passed=True,
            trend_status=trend_status,
        )

    return EvaluationQualityHealth(
        healthy=True,
        status="healthy",
        latest_run_id=latest_run.id,
        quality_gate_passed=True,
        trend_status=trend_status,
    )


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
