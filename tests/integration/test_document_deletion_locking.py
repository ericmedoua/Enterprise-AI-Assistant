import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.database.session import SessionLocal, engine
from app.models.document import Document
from app.models.user import User
from app.repositories.document_repository import DocumentRepository


@pytest.mark.integration
def test_postgres_skips_document_locked_by_another_session(test_user):
    """A second PostgreSQL session must skip a document locked by the first."""
    if engine.dialect.name != "postgresql":
        pytest.skip("This concurrency test requires PostgreSQL.")

    document_id = str(uuid.uuid4())
    stored_filename = f"{document_id}_locking-test.pdf"

    with SessionLocal() as setup_db:
        document = Document(
            id=document_id,
            owner_id=test_user.id,
            filename="locking-test.pdf",
            stored_filename=stored_filename,
            status="deleting",
            chunk_count=0,
        )
        setup_db.add(document)
        setup_db.commit()

    first_db = SessionLocal()
    second_db = SessionLocal()

    try:
        first_claim = DocumentRepository(first_db).claim_pending_deletion(
            document_id,
            owner_id=test_user.id,
        )
        assert first_claim is not None
        assert first_claim.id == document_id

        # The first transaction still holds the row lock.
        second_claim = DocumentRepository(second_db).claim_pending_deletion(
            document_id,
            owner_id=test_user.id,
        )
        assert second_claim is None

        # Releasing the first transaction should make the row claimable.
        first_db.rollback()

        second_claim_after_release = DocumentRepository(
            second_db
        ).claim_pending_deletion(
            document_id,
            owner_id=test_user.id,
        )
        assert second_claim_after_release is not None
        assert second_claim_after_release.id == document_id

    finally:
        first_db.rollback()
        second_db.rollback()
        first_db.close()
        second_db.close()

        # Remove only the test's own record.
        with SessionLocal() as cleanup_db:
            cleanup_db.execute(
                Document.__table__.delete().where(
                    Document.id == document_id,
                    Document.owner_id == test_user.id,
                )
            )
            cleanup_db.commit()
