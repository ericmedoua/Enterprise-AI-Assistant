from unittest.mock import Mock, patch

import pytest


@pytest.mark.asyncio
@patch("app.main.asyncio.create_task")
@patch("app.main.run_remediation_scheduler")
async def test_startup_enables_scheduler(
    mock_scheduler,
    mock_create_task,
):
    from app.main import startup

    mock_create_task.side_effect = lambda coroutine: coroutine.close()

    with (
        patch(
            "app.main.settings.evaluation_scheduler_enabled",
            True,
        ),
        patch(
            "app.main.settings.evaluation_scheduler_interval_seconds",
            300,
        ),
    ):
        await startup()

    mock_create_task.assert_called_once()
    mock_scheduler.assert_called_once_with(
        interval_seconds=300,
    )


@pytest.mark.asyncio
@patch("app.main.asyncio.create_task")
@patch("app.main.run_remediation_scheduler")
async def test_startup_disables_scheduler(
    mock_scheduler,
    mock_create_task,
):
    from app.main import startup

    with patch(
        "app.main.settings.evaluation_scheduler_enabled",
        False,
    ):
        await startup()

    mock_create_task.assert_not_called()
    mock_scheduler.assert_not_called()
