from sqlalchemy.orm import Session

from app.models.document import Document


DOCUMENT_STATUSES = {"indexing", "indexed", "failed"}

ALLOWED_STATUS_TRANSITIONS = {
    "indexing": {"indexed", "failed"},
    "indexed": set(),
    "failed": set(),
}


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
                raise ValueError(
                    f"Invalid document status transition: {document.status} -> {status}"
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
