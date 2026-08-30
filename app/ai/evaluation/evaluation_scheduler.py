import asyncio

from app.ai.evaluation.evaluation_remediation_job import (
    run_stale_evaluation_remediation,
)
from app.core.logger import app_logger


async def run_remediation_scheduler(
    interval_seconds: int = 300,
) -> None:
    """
    Periodically run stale-evaluation remediation.

    The scheduler continues running until cancelled.
    """

    while True:
        try:
            run_stale_evaluation_remediation()

        except Exception:
            app_logger.exception("Stale evaluation remediation job failed.")

        await asyncio.sleep(interval_seconds)
