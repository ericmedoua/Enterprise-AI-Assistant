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
