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


def test_delete_owned_document_removes_record(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    deleted = repository.delete_owned_document(document.id, test_user.id)

    assert deleted is True
    assert repository.get_owned_document(document.id, test_user.id) is None


def test_delete_owned_document_does_not_remove_another_users_record(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    deleted = repository.delete_owned_document(document.id, test_user.id + 1)

    assert deleted is False
    assert repository.get_owned_document(document.id, test_user.id) is not None


def test_begin_deletion_marks_indexed_document_as_deleting(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    repository.update_status(document.id, "indexed", chunk_count=7)

    deleting = repository.begin_deletion(document.id, test_user.id)

    assert deleting is not None
    assert deleting.status == "deleting"
    assert deleting.chunk_count == 7


def test_begin_deletion_allows_retry(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    repository.update_status(document.id, "indexed", chunk_count=3)
    repository.begin_deletion(document.id, test_user.id)

    retry = repository.begin_deletion(document.id, test_user.id)

    assert retry is not None
    assert retry.status == "deleting"


def test_begin_deletion_rejects_indexing_document(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    with pytest.raises(ValueError, match="while it is indexing"):
        repository.begin_deletion(document.id, test_user.id)

    assert repository.get_owned_document(document.id, test_user.id).status == "indexing"


def test_begin_deletion_does_not_change_another_users_document(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    result = repository.begin_deletion(document.id, test_user.id + 1)

    assert result is None
    assert repository.get_owned_document(document.id, test_user.id).status == "indexing"


def test_failed_document_can_enter_deleting_state(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    repository.update_status(
        document.id,
        "failed",
        error_message="Indexing failed.",
    )

    deleting = repository.begin_deletion(document.id, test_user.id)

    assert deleting is not None
    assert deleting.status == "deleting"
    assert deleting.error_message == "Indexing failed."


def test_list_pending_deletions_only_returns_deleting_documents(db, test_user):
    repository = DocumentRepository(db)

    pending = create_document(repository, test_user.id, "pending.pdf")
    indexed = create_document(repository, test_user.id, "indexed.pdf")
    failed = create_document(repository, test_user.id, "failed.pdf")

    repository.update_status(pending.id, "failed")
    repository.begin_deletion(pending.id, test_user.id)

    repository.update_status(indexed.id, "indexed", chunk_count=3)

    repository.update_status(
        failed.id,
        "failed",
        error_message="Indexing failed.",
    )

    documents = repository.list_pending_deletions()

    assert pending.id in {document.id for document in documents}
    assert all(document.status == "deleting" for document in documents)
    assert documents[0].status == "deleting"


def test_list_pending_deletions_respects_limit(db, test_user):
    repository = DocumentRepository(db)
    created_documents = [
        create_document(repository, test_user.id, f"pending-{index}.pdf")
        for index in range(3)
    ]

    for document in created_documents:
        repository.update_status(document.id, "failed")
        repository.begin_deletion(document.id, test_user.id)

    documents = repository.list_pending_deletions(limit=2)

    assert len(documents) == 2
    assert all(document.status == "deleting" for document in documents)


def test_list_pending_deletions_rejects_nonpositive_limit(db):
    repository = DocumentRepository(db)

    for invalid_limit in (0, -1):
        with pytest.raises(
            ValueError, match="limit must be greater than or equal to 1"
        ):
            repository.list_pending_deletions(limit=invalid_limit)


def test_list_pending_deletions_returns_empty_list_when_none_pending(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    documents = repository.list_pending_deletions()

    assert document.id not in {item.id for item in documents}
