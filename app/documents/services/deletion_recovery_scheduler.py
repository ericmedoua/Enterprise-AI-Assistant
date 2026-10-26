import asyncio
import logging

from app.documents.services.deletion_recovery_service import (
    DocumentDeletionRecoveryService,
)

logger = logging.getLogger(__name__)


async def run_document_deletion_recovery_scheduler(
    interval_seconds: int = 300,
) -> None:
    """Periodically retry cleanup of documents stuck in deleting status."""
    if interval_seconds < 1:
        raise ValueError("interval_seconds must be greater than or equal to 1.")

    while True:
        try:
            completed = await asyncio.to_thread(
                DocumentDeletionRecoveryService().recover_pending_deletions
            )
            if completed:
                logger.info(
                    "Document deletion recovery completed %s document(s).",
                    completed,
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Document deletion recovery cycle failed.")

        await asyncio.sleep(interval_seconds)
