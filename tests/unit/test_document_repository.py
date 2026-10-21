import uuid

import pytest

from app.repositories.document_repository import DocumentRepository


def create_document(repository, owner_id, filename="report.pdf"):
    document_id = str(uuid.uuid4())

    return repository.create_document(
        document_id=document_id,
        owner_id=owner_id,
        filename=filename,
        stored_filename=f"{document_id}_{filename}",
    )


def test_create_document_starts_in_indexing_state(db, test_user):
    repository = DocumentRepository(db)

    document = create_document(repository, test_user.id)

    assert document.status == "indexing"
    assert document.chunk_count == 0
    assert document.error_message is None
    assert document.owner_id == test_user.id
    assert document.filename == "report.pdf"


def test_get_owned_document_does_not_return_another_users_document(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    assert repository.get_owned_document(document.id, test_user.id) is not None
    assert repository.get_owned_document(document.id, test_user.id + 1) is None


def test_list_by_owner_only_returns_that_users_documents(db, test_user):
    repository = DocumentRepository(db)
    first = create_document(repository, test_user.id, "first.pdf")
    second = create_document(repository, test_user.id, "second.pdf")

    documents = repository.list_by_owner(test_user.id)
    document_ids = {document.id for document in documents}

    assert first.id in document_ids
    assert second.id in document_ids
    assert all(document.owner_id == test_user.id for document in documents)


def test_update_status_to_indexed_persists_chunk_count(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    updated = repository.update_status(
        document.id,
        "indexed",
        chunk_count=7,
    )

    assert updated is not None
    assert updated.status == "indexed"
    assert updated.chunk_count == 7
    assert updated.error_message is None


def test_update_status_to_failed_persists_error(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    updated = repository.update_status(
        document.id,
        "failed",
        error_message="Document processing failed.",
    )

    assert updated is not None
    assert updated.status == "failed"
    assert updated.error_message == "Document processing failed."
    assert updated.chunk_count == 0


def test_invalid_status_transition_is_rejected(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    repository.update_status(document.id, "indexed", chunk_count=3)

    with pytest.raises(ValueError, match="Invalid document status transition"):
        repository.update_status(document.id, "failed")


def test_indexed_status_requires_chunk_count(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    with pytest.raises(ValueError, match="chunk_count is required"):
        repository.update_status(document.id, "indexed")
