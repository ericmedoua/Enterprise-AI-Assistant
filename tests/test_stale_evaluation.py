from datetime import datetime, timedelta, timezone

from app.ai.evaluation.stale_evaluation import (
    is_evaluation_stale,
)


def test_completed_run_is_not_stale():
    started = datetime.now(timezone.utc) - timedelta(minutes=10)

    assert (
        is_evaluation_stale(
            status="completed",
            started_at=started,
            timeout_seconds=300,
        )
        is False
    )


def test_running_run_without_started_at_is_not_stale():
    assert (
        is_evaluation_stale(
            status="running",
            started_at=None,
            timeout_seconds=300,
        )
        is False
    )


def test_recent_running_run_is_not_stale():
    started = datetime.now(timezone.utc) - timedelta(seconds=30)

    assert (
        is_evaluation_stale(
            status="running",
            started_at=started,
            timeout_seconds=300,
        )
        is False
    )


def test_old_running_run_is_stale():
    started = datetime.now(timezone.utc) - timedelta(seconds=600)

    assert (
        is_evaluation_stale(
            status="running",
            started_at=started,
            timeout_seconds=300,
        )
        is True
    )
