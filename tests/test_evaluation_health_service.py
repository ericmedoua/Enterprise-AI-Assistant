from datetime import datetime, timezone
from unittest.mock import Mock

from app.ai.evaluation.evaluation_health_service import (
    build_evaluation_health,
)


def test_build_evaluation_health_uses_repository_and_evaluates_health():
    repository = Mock()

    running_run = Mock(
        status="running",
        started_at=datetime.now(timezone.utc),
    )

    repository.list_running_runs.return_value = [running_run]
    repository.count_cancelled_runs.return_value = 3

    result = build_evaluation_health(repository)

    assert result.healthy is True
    assert result.running_count == 1
    assert result.stale_count == 0
    assert result.cancelled_count == 3

    repository.list_running_runs.assert_called_once()
    repository.count_cancelled_runs.assert_called_once()
