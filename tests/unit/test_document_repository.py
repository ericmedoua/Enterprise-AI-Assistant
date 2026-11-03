import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.repositories.document_repository import (
    DELETION_RETRY_DELAYS_MINUTES,
    DocumentRepository,
    get_deletion_retry_delay,
)
from app.models.document import Document


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


def test_deleting_document_cannot_return_to_indexed(db, test_user):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    repository.update_status(document.id, "indexed", chunk_count=3)
    repository.begin_deletion(document.id, test_user.id)

    with pytest.raises(
        ValueError,
        match="Invalid document status transition: deleting -> indexed",
    ):
        repository.update_status(document.id, "indexed", chunk_count=3)

    db.expire_all()
    persisted = repository.get_owned_document(document.id, test_user.id)

    assert persisted is not None
    assert persisted.status == "deleting"


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

    documents = repository.list_pending_deletions(limit=10000)

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


def test_new_document_starts_with_zero_deletion_attempts(db, test_user):
    repository = DocumentRepository(db)

    document = create_document(repository, test_user.id)

    assert document.deletion_attempts == 0
    assert document.deletion_next_retry_at is None


@pytest.mark.parametrize(
    ("attempt", "expected_minutes"),
    [
        (1, 1),
        (2, 2),
        (3, 4),
        (4, 8),
        (5, 15),
        (6, 15),
        (10, 15),
    ],
)
def test_deletion_retry_delay_uses_capped_exponential_backoff(
    attempt,
    expected_minutes,
):
    delay = get_deletion_retry_delay(attempt)

    assert delay == timedelta(minutes=expected_minutes)


def test_deletion_retry_delay_rejects_invalid_attempt():
    with pytest.raises(ValueError, match="attempt must be greater than or equal to 1"):
        get_deletion_retry_delay(0)


def test_record_deletion_failure_increments_attempt_and_schedules_retry(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)
    repository.update_status(document.id, "failed")
    repository.begin_deletion(document.id, test_user.id)

    before = datetime.now(timezone.utc)
    retry_at = repository.record_deletion_failure(document.id)
    after = datetime.now(timezone.utc)

    db.refresh(document)

    assert document.deletion_attempts == 1
    assert retry_at is not None
    assert before + timedelta(minutes=1) <= retry_at
    assert retry_at <= after + timedelta(minutes=1)
    assert document.deletion_next_retry_at == retry_at


def test_record_deletion_failure_ignores_missing_or_non_deleting_document(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    assert repository.record_deletion_failure(document.id) is None

    db.refresh(document)
    assert document.deletion_attempts == 0
    assert document.deletion_next_retry_at is None

    assert repository.record_deletion_failure("missing-document-id") is None


def test_list_pending_deletions_excludes_documents_with_future_retry(
    db,
    test_user,
):
    repository = DocumentRepository(db)

    first = create_document(repository, test_user.id, "first.pdf")
    second = create_document(repository, test_user.id, "second.pdf")

    for document in (first, second):
        repository.update_status(document.id, "failed")
        repository.begin_deletion(document.id, test_user.id)

    retry_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    second.deletion_attempts = 1
    second.deletion_next_retry_at = retry_at
    db.commit()

    pending_ids = {
        document.id for document in repository.list_pending_deletions(limit=10_000)
    }

    assert first.id in pending_ids
    assert second.id not in pending_ids


def test_list_pending_deletions_includes_document_when_retry_is_due(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    document = create_document(repository, test_user.id)

    repository.update_status(document.id, "failed")
    repository.begin_deletion(document.id, test_user.id)

    document.deletion_attempts = 1
    document.deletion_next_retry_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()

    pending_ids = {item.id for item in repository.list_pending_deletions(limit=10_000)}

    assert document.id in pending_ids


def test_document_health_metrics_is_stable_without_database_changes(db):
    repository = DocumentRepository(db)

    before = repository.get_document_health_metrics()
    after = repository.get_document_health_metrics()

    assert after == before


def test_document_health_metrics_counts_lifecycle_and_retry_states(
    db,
    test_user,
):
    repository = DocumentRepository(db)
    baseline = repository.get_document_health_metrics()

    indexing = create_document(repository, test_user.id, "indexing.pdf")

    indexed = create_document(repository, test_user.id, "indexed.pdf")
    repository.update_status(indexed.id, "indexed", chunk_count=5)

    failed = create_document(repository, test_user.id, "failed.pdf")
    repository.update_status(
        failed.id,
        "failed",
        error_message="Indexing failed.",
    )

    due_without_schedule = create_document(
        repository, test_user.id, "due-no-schedule.pdf"
    )
    repository.update_status(due_without_schedule.id, "failed")
    repository.begin_deletion(due_without_schedule.id, test_user.id)

    due_with_past_schedule = create_document(repository, test_user.id, "due-past.pdf")
    repository.update_status(due_with_past_schedule.id, "failed")
    repository.begin_deletion(due_with_past_schedule.id, test_user.id)
    due_with_past_schedule.deletion_attempts = 2
    due_with_past_schedule.deletion_next_retry_at = datetime.now(
        timezone.utc
    ) - timedelta(minutes=1)

    scheduled = create_document(repository, test_user.id, "scheduled.pdf")
    repository.update_status(scheduled.id, "failed")
    repository.begin_deletion(scheduled.id, test_user.id)
    scheduled.deletion_attempts = 3
    scheduled.deletion_next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # A retry timestamp on a non-deleting document must not count.
    indexed.deletion_attempts = 4
    indexed.deletion_next_retry_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.commit()

    metrics = repository.get_document_health_metrics()

    assert metrics == {
        "total_documents": baseline["total_documents"] + 6,
        "indexing_count": baseline["indexing_count"] + 1,
        "indexed_count": baseline["indexed_count"] + 1,
        "failed_count": baseline["failed_count"] + 1,
        "deleting_count": baseline["deleting_count"] + 3,
        "deletion_due_count": baseline["deletion_due_count"] + 2,
        "deletion_scheduled_count": (baseline["deletion_scheduled_count"] + 1),
        "total_deletion_attempts": (baseline["total_deletion_attempts"] + 9),
    }
