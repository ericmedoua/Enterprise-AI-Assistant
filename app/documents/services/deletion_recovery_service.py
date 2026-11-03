import logging
from dataclasses import dataclass
from pathlib import Path

from app.ai.retrieval.dependencies import get_chroma_service
from app.database.session import SessionLocal
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeletionRecoveryResult:
    """Outcome counts for one document deletion recovery cycle."""

    discovered: int = 0
    completed: int = 0
    skipped: int = 0
    cleanup_failed: int = 0
    retry_scheduled: int = 0
    retry_schedule_failed: int = 0


class DocumentDeletionRecoveryService:
    """Retry cleanup for documents left in the deleting state."""

    def __init__(
        self,
        *,
        session_factory=None,
        chroma_service_factory=None,
        upload_directory: Path | None = None,
        batch_size: int = 100,
    ):
        if batch_size < 1:
            raise ValueError("batch_size must be greater than or equal to 1.")

        self.session_factory = session_factory or SessionLocal
        self.chroma_service_factory = chroma_service_factory or get_chroma_service
        self.upload_directory = upload_directory or Path("storage")
        self.batch_size = batch_size

    def recover_pending_deletions(self) -> DeletionRecoveryResult:
        """Clean up pending documents and report this cycle's outcomes."""
        # Read candidate IDs only. This query does not claim the documents.
        with self.session_factory() as db:
            pending_ids = [
                document.id
                for document in DocumentRepository(db).list_pending_deletions(
                    limit=self.batch_size
                )
            ]

        completed = 0
        skipped = 0
        cleanup_failed = 0
        retry_scheduled = 0
        retry_schedule_failed = 0

        for document_id in pending_ids:
            failure = False

            try:
                # Claim one document and keep this session open during cleanup.
                with self.session_factory() as db:
                    repository = DocumentRepository(db)
                    document = repository.claim_pending_deletion(document_id)

                    # Another worker may hold the lock, or the record may be gone.
                    if document is None:
                        skipped += 1
                        continue

                    owner_id = document.owner_id
                    stored_filename = document.stored_filename

                    storage_root = self.upload_directory.resolve()
                    file_path = (storage_root / stored_filename).resolve()

                    # Stored documents must be direct children of the storage root.
                    if (
                        file_path.parent != storage_root
                        or file_path.name != stored_filename
                    ):
                        raise ValueError(
                            f"Unsafe storage path for document {document_id}"
                        )

                    # Use the recorded owner, not the current request's identity.
                    self.chroma_service_factory().delete_document(
                        owner_id=owner_id,
                        document_id=document_id,
                    )

                    # Missing files are safe: a previous attempt may have removed them.
                    file_path.unlink(missing_ok=True)

                    deleted = repository.delete_owned_document(
                        document_id,
                        owner_id,
                    )

                    if deleted:
                        completed += 1
                    else:
                        skipped += 1
                        logger.info(
                            "Document record was already removed during recovery: "
                            "document_id=%s",
                            document_id,
                        )

            except Exception:
                cleanup_failed += 1
                failure = True
                logger.exception(
                    "Document deletion recovery failed: document_id=%s",
                    document_id,
                )

            # The cleanup session has now closed and released its row lock.
            if failure:
                try:
                    with self.session_factory() as db:
                        DocumentRepository(db).record_deletion_failure(document_id)
                    retry_scheduled += 1
                except Exception:
                    retry_schedule_failed += 1
                    logger.exception(
                        "Could not schedule document deletion retry: document_id=%s",
                        document_id,
                    )

        return DeletionRecoveryResult(
            discovered=len(pending_ids),
            completed=completed,
            skipped=skipped,
            cleanup_failed=cleanup_failed,
            retry_scheduled=retry_scheduled,
            retry_schedule_failed=retry_schedule_failed,
        )
