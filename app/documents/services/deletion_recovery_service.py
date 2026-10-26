import logging
from pathlib import Path

from app.ai.retrieval.dependencies import get_chroma_service
from app.database.session import SessionLocal
from app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


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

    def recover_pending_deletions(self) -> int:
        """Clean up pending documents and return the number completed."""
        with self.session_factory() as db:
            pending = [
                (document.id, document.owner_id, document.stored_filename)
                for document in DocumentRepository(db).list_pending_deletions(
                    limit=self.batch_size
                )
            ]

        completed = 0

        for document_id, owner_id, stored_filename in pending:
            try:
                storage_root = self.upload_directory.resolve()
                file_path = (storage_root / stored_filename).resolve()

                # Stored documents must be direct children of the storage root.
                if (
                    file_path.parent != storage_root
                    or file_path.name != stored_filename
                ):
                    raise ValueError(f"Unsafe storage path for document {document_id}")

                # Use the recorded owner, not the current request's identity.
                self.chroma_service_factory().delete_document(
                    owner_id=owner_id,
                    document_id=document_id,
                )

                # Missing files are safe: a previous attempt may have removed them.
                file_path.unlink(missing_ok=True)

                with self.session_factory() as db:
                    deleted = DocumentRepository(db).delete_owned_document(
                        document_id,
                        owner_id,
                    )

                    if deleted:
                        completed += 1
                    else:
                        logger.info(
                            "Document record was already removed during recovery: document_id=%s",
                            document_id,
                        )
                        completed += 1

            except Exception:
                # One failure must not prevent recovery of other documents.
                logger.exception(
                    "Document deletion recovery failed: document_id=%s",
                    document_id,
                )

        return completed
