import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import settings
from app.main import app, startup, shutdown


@pytest.mark.asyncio
async def test_startup_disables_document_recovery_scheduler_by_default(
    monkeypatch,
):
    monkeypatch.setattr(settings, "evaluation_scheduler_enabled", False)
    monkeypatch.setattr(settings, "document_deletion_recovery_enabled", False)

    await startup()

    tasks = app.state.scheduler_tasks

    try:
        assert tasks == []
    finally:
        await shutdown()


@pytest.mark.asyncio
async def test_startup_starts_document_recovery_scheduler_when_enabled(
    monkeypatch,
):
    scheduler = AsyncMock()

    monkeypatch.setattr(settings, "evaluation_scheduler_enabled", False)
    monkeypatch.setattr(settings, "document_deletion_recovery_enabled", True)
    monkeypatch.setattr(
        settings,
        "document_deletion_recovery_interval_seconds",
        30,
    )

    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_scheduler."
        "run_document_deletion_recovery_scheduler",
        scheduler,
    )

    await startup()

    tasks = app.state.scheduler_tasks

    try:
        assert len(tasks) == 1
        assert tasks[0].get_name() == "document-deletion-recovery-scheduler"
        await asyncio.sleep(0)
        scheduler.assert_awaited_once_with(interval_seconds=30)
    finally:
        await shutdown()


@pytest.mark.asyncio
async def test_shutdown_cancels_scheduler_tasks(monkeypatch):
    task = MagicMock()
    task.cancel = MagicMock()

    app.state.scheduler_tasks = [task]

    async def fake_gather(*tasks, return_exceptions=False):
        assert return_exceptions is True
        assert tasks == (task,)

    monkeypatch.setattr(asyncio, "gather", fake_gather)

    await shutdown()

    task.cancel.assert_called_once()


@pytest.mark.asyncio
async def test_scheduler_continues_after_recovery_exception(monkeypatch):
    from app.documents.services import deletion_recovery_scheduler

    recovery_service = MagicMock()
    recovery_service.recover_pending_deletions.side_effect = [
        RuntimeError("Temporary database failure"),
        1,
    ]

    monkeypatch.setattr(
        deletion_recovery_scheduler,
        "DocumentDeletionRecoveryService",
        MagicMock(return_value=recovery_service),
    )

    sleep_calls = []

    async def fake_sleep(interval):
        sleep_calls.append(interval)

        # Stop after the second recovery cycle.
        if len(sleep_calls) == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(
        deletion_recovery_scheduler.asyncio,
        "sleep",
        fake_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await deletion_recovery_scheduler.run_document_deletion_recovery_scheduler(
            interval_seconds=10,
        )

    assert recovery_service.recover_pending_deletions.call_count == 2
    assert sleep_calls == [10, 10]


@pytest.mark.asyncio
async def test_scheduler_propagates_cancellation_during_sleep(monkeypatch):
    from app.documents.services import deletion_recovery_scheduler

    recovery_service = MagicMock()
    recovery_service.recover_pending_deletions.return_value = 0

    monkeypatch.setattr(
        deletion_recovery_scheduler,
        "DocumentDeletionRecoveryService",
        MagicMock(return_value=recovery_service),
    )

    sleep_started = asyncio.Event()

    async def blocking_sleep(interval):
        sleep_started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(
        deletion_recovery_scheduler.asyncio,
        "sleep",
        blocking_sleep,
    )

    task = asyncio.create_task(
        deletion_recovery_scheduler.run_document_deletion_recovery_scheduler(
            interval_seconds=10,
        )
    )

    await sleep_started.wait()
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    recovery_service.recover_pending_deletions.assert_called_once()
