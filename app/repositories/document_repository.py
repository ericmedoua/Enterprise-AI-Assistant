from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.document import Document


DOCUMENT_STATUSES = {"indexing", "indexed", "failed", "deleting"}

ALLOWED_STATUS_TRANSITIONS = {
    "indexing": {"indexed", "failed"},
    "indexed": {"deleting"},
    "failed": {"deleting"},
    "deleting": set(),
}

DELETION_RETRY_DELAYS_MINUTES = (1, 2, 4, 8, 15)


class InvalidDocumentStatusTransition(ValueError):
    """Raised when a document status transition is not allowed."""

    def __init__(self, current_status: str, requested_status: str):
        self.current_status = current_status
        self.requested_status = requested_status

        super().__init__(
            f"Invalid document status transition: "
            f"{current_status} -> {requested_status}"
        )


def get_deletion_retry_delay(attempt: int) -> timedelta:
    """Return the capped exponential backoff for a deletion attempt."""
    if attempt < 1:
        raise ValueError("attempt must be greater than or equal to 1.")

    delay_index = min(
        attempt - 1,
        len(DELETION_RETRY_DELAYS_MINUTES) - 1,
    )

    return timedelta(minutes=DELETION_RETRY_DELAYS_MINUTES[delay_index])


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        *,
        document_id: str,
        owner_id: int,
        filename: str,
        stored_filename: str,
    ) -> Document:
        document = Document(
            id=document_id,
            owner_id=owner_id,
            filename=filename,
            stored_filename=stored_filename,
            status="indexing",
            chunk_count=0,
        )

        try:
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise

        return document

    def get_owned_document(
        self,
        document_id: str,
        owner_id: int,
    ) -> Document | None:
        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id,
                Document.owner_id == owner_id,
            )
            .first()
        )

    def list_by_owner(self, owner_id: int) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.owner_id == owner_id)
            .order_by(
                Document.created_at.desc(),
                Document.id.desc(),
            )
            .all()
        )

    def update_status(
        self,
        document_id: str,
        status: str,
        *,
        chunk_count: int | None = None,
        error_message: str | None = None,
    ) -> Document | None:
        if status not in DOCUMENT_STATUSES:
            raise ValueError(f"Invalid document status: {status}")

        if chunk_count is not None and chunk_count < 0:
            raise ValueError("chunk_count must be greater than or equal to 0.")

        document = self.db.get(Document, document_id)

        if document is None:
            return None

        if status != document.status:
            allowed = ALLOWED_STATUS_TRANSITIONS[document.status]
            if status not in allowed:
                raise InvalidDocumentStatusTransition(
                    current_status=document.status,
                    requested_status=status,
                )

        if status == "indexed" and chunk_count is None:
            raise ValueError("chunk_count is required when status is indexed.")

        document.status = status

        if chunk_count is not None:
            document.chunk_count = chunk_count

        if status == "indexed":
            document.error_message = None
        elif status == "failed":
            document.error_message = error_message or "Document indexing failed."

            document.chunk_count = 0

        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise

        return document

    def begin_deletion(
        self,
        document_id: str,
        owner_id: int,
    ) -> Document | None:
        """Mark an owned document as deleting before external cleanup.

        Repeated calls for a document already being deleted are allowed,
        so a failed cleanup can be retried.
        """
        try:
            document = (
                self.db.query(Document)
                .filter(
                    Document.id == document_id,
                    Document.owner_id == owner_id,
                )
                .with_for_update()
                .first()
            )

            if document is None:
                self.db.rollback()
                return None

            if document.status == "indexing":
                raise ValueError("Cannot delete a document while it is indexing.")

            if document.status not in {"indexed", "failed", "deleting"}:
                raise ValueError(f"Cannot delete document in status: {document.status}")

            if document.status != "deleting":
                document.status = "deleting"

            # Commit even on a retry to release the row lock.
            self.db.commit()
            self.db.refresh(document)
            return document

        except Exception:
            self.db.rollback()
            raise

    def claim_pending_deletion(
        self,
        document_id: str,
        owner_id: int | None = None,
    ) -> Document | None:
        """Lock a pending deletion so only one worker cleans it up at a time."""
        try:
            query = self.db.query(Document).filter(
                Document.id == document_id,
                Document.status == "deleting",
            )

            if owner_id is not None:
                query = query.filter(Document.owner_id == owner_id)

            return query.with_for_update(skip_locked=True).first()

        except Exception:
            self.db.rollback()
            raise

    def delete_owned_document(
        self,
        document_id: str,
        owner_id: int,
    ) -> bool:
        """Delete a document record only if it belongs to the given owner."""
        document = self.get_owned_document(document_id, owner_id)

        if document is None:
            return False

        try:
            self.db.delete(document)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return True

    def list_pending_deletions(self, limit: int = 100) -> list[Document]:
        """Return deleting documents whose retry time has arrived."""
        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1.")

        now = datetime.now(timezone.utc)

        return (
            self.db.query(Document)
            .filter(
                Document.status == "deleting",
                or_(
                    Document.deletion_next_retry_at.is_(None),
                    Document.deletion_next_retry_at <= now,
                ),
            )
            .order_by(Document.created_at.asc(), Document.id.asc())
            .limit(limit)
            .all()
        )

    def record_deletion_failure(self, document_id: str) -> datetime | None:
        """Record a failed cleanup and schedule its next retry."""
        try:
            document = (
                self.db.query(Document)
                .filter(
                    Document.id == document_id,
                    Document.status == "deleting",
                )
                .with_for_update()
                .first()
            )

            if document is None:
                self.db.rollback()
                return None

            document.deletion_attempts += 1
            retry_at = datetime.now(timezone.utc) + get_deletion_retry_delay(
                document.deletion_attempts
            )
            document.deletion_next_retry_at = retry_at

            self.db.commit()
            return retry_at

        except Exception:
            self.db.rollback()
            raise
