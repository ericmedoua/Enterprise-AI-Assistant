import asyncio
from unittest.mock import patch

import pytest

from app.ai.evaluation.evaluation_scheduler import (
    run_remediation_scheduler,
)


@pytest.mark.asyncio
@patch("app.ai.evaluation.evaluation_scheduler.asyncio.sleep")
@patch("app.ai.evaluation.evaluation_scheduler.run_stale_evaluation_remediation")
async def test_scheduler_runs_remediation(
    mock_remediation,
    mock_sleep,
):
    async def stop_scheduler(
        interval_seconds,
    ):
        raise asyncio.CancelledError

    mock_sleep.side_effect = stop_scheduler

    mock_remediation.return_value = []

    with pytest.raises(asyncio.CancelledError):
        await run_remediation_scheduler(interval_seconds=300)

    mock_remediation.assert_called_once()

    mock_sleep.assert_called_once_with(300)


@pytest.mark.asyncio
@patch("app.ai.evaluation.evaluation_scheduler.asyncio.sleep")
@patch("app.ai.evaluation.evaluation_scheduler.app_logger")
@patch("app.ai.evaluation.evaluation_scheduler.run_stale_evaluation_remediation")
async def test_scheduler_continues_after_job_failure(
    mock_remediation,
    mock_logger,
    mock_sleep,
):
    calls = 0

    def remediation():
        nonlocal calls

        calls += 1

        if calls == 1:
            raise RuntimeError("remediation failed")

        return []

    mock_remediation.side_effect = remediation

    async def stop_after_two_runs(
        interval_seconds,
    ):
        if calls >= 2:
            raise asyncio.CancelledError

    mock_sleep.side_effect = stop_after_two_runs

    with pytest.raises(asyncio.CancelledError):
        await run_remediation_scheduler(interval_seconds=300)

    assert calls == 2

    mock_logger.exception.assert_called_once_with(
        "Stale evaluation remediation job failed."
    )
