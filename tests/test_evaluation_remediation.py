from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from app.ai.evaluation.evaluation_remediation import (
    remediate_stale_evaluations,
)


def test_remediate_stale_evaluations():
    stale_run = Mock(
        id=25,
        status="running",
        started_at=(datetime.now(timezone.utc) - timedelta(hours=1)),
    )

    fresh_run = Mock(
        id=26,
        status="running",
        started_at=datetime.now(timezone.utc),
    )

    repository = Mock()

    repository.list_running_runs.return_value = [
        stale_run,
        fresh_run,
    ]

    repository.fail_stale_run.side_effect = lambda run_id, timeout_seconds: (
        stale_run if run_id == 25 else None
    )

    result = remediate_stale_evaluations(
        repository=repository,
        timeout_seconds=300,
    )

    assert result == [25]

    repository.fail_stale_run.assert_called_once_with(
        run_id=25,
        timeout_seconds=300,
    )


def test_remediate_stale_evaluations_when_none_stale():
    repository = Mock()

    repository.list_running_runs.return_value = []

    result = remediate_stale_evaluations(
        repository=repository,
        timeout_seconds=300,
    )

    assert result == []

    repository.fail_stale_run.assert_not_called()
