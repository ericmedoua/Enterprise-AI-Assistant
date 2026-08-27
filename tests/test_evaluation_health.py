from datetime import datetime, timedelta, timezone

from app.ai.evaluation.evaluation_health import (
    evaluate_health,
)


def test_evaluation_health_is_healthy():
    runs = [
        type(
            "Run",
            (),
            {
                "status": "running",
                "started_at": datetime.now(timezone.utc),
            },
        )()
    ]

    result = evaluate_health(
        runs,
        timeout_seconds=300,
    )

    assert result.healthy is True
    assert result.running_count == 1
    assert result.stale_count == 0


def test_evaluation_health_detects_stale_run():
    runs = [
        type(
            "Run",
            (),
            {
                "status": "running",
                "started_at": (datetime.now(timezone.utc) - timedelta(minutes=10)),
            },
        )()
    ]

    result = evaluate_health(
        runs,
        timeout_seconds=300,
    )

    assert result.healthy is False
    assert result.running_count == 1
    assert result.stale_count == 1


def test_evaluation_health_with_no_running_runs():
    result = evaluate_health(
        [],
        timeout_seconds=300,
    )

    assert result.healthy is True
    assert result.running_count == 0
    assert result.stale_count == 0
