from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.documents.services.deletion_recovery_service import (
    DocumentDeletionRecoveryService,
)


@pytest.fixture
def recovery_setup(tmp_path):
    session = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = session

    repository = MagicMock()
    repository.list_pending_deletions.return_value = []
    repository_class = MagicMock(return_value=repository)

    chroma = MagicMock()
    chroma_factory = MagicMock(return_value=chroma)

    service = DocumentDeletionRecoveryService(
        session_factory=session_factory,
        chroma_service_factory=chroma_factory,
        upload_directory=tmp_path,
        batch_size=10,
    )

    return service, session_factory, repository, chroma, tmp_path


def test_recovery_returns_zero_when_no_documents_are_pending(
    recovery_setup,
    monkeypatch,
):
    service, _, repository, chroma, _ = recovery_setup

    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        lambda db: repository,
    )

    assert service.recover_pending_deletions() == 0
    chroma.delete_document.assert_not_called()


def test_recovery_removes_vectors_file_and_record(
    recovery_setup,
    monkeypatch,
):
    service, session_factory, repository, chroma, storage = recovery_setup
    document = SimpleNamespace(
        id="doc-1",
        owner_id=101,
        stored_filename="doc-1_report.pdf",
    )
    repository.list_pending_deletions.return_value = [document]
    repository.claim_pending_deletion.return_value = document
    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        lambda db: repository,
    )

    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")

    assert service.recover_pending_deletions() == 1

    chroma.delete_document.assert_called_once_with(
        owner_id=101,
        document_id="doc-1",
    )
    assert not file_path.exists()
    repository.delete_owned_document.assert_called_once_with("doc-1", 101)
    assert session_factory.call_count == 2


def test_recovery_keeps_record_when_chroma_fails(
    recovery_setup,
    monkeypatch,
):
    service, _, repository, chroma, storage = recovery_setup
    document = SimpleNamespace(
        id="doc-2",
        owner_id=202,
        stored_filename="doc-2_report.pdf",
    )
    repository.list_pending_deletions.return_value = [document]
    repository.claim_pending_deletion.return_value = document
    repository_class = lambda db: repository
    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        repository_class,
    )
    chroma.delete_document.side_effect = RuntimeError("Chroma unavailable")

    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")

    assert service.recover_pending_deletions() == 0

    assert file_path.exists()
    repository.delete_owned_document.assert_not_called()


def test_recovery_keeps_record_when_file_deletion_fails(
    recovery_setup,
    monkeypatch,
):
    service, _, repository, chroma, storage = recovery_setup
    document = SimpleNamespace(
        id="doc-file-error",
        owner_id=303,
        stored_filename="doc-file-error_report.pdf",
    )
    repository.list_pending_deletions.return_value = [document]
    repository.claim_pending_deletion.return_value = document

    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        lambda db: repository,
    )

    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")

    # Simulate an operating-system error while removing this file.
    from pathlib import Path

    original_unlink = Path.unlink

    def failing_unlink(path, *args, **kwargs):
        if path == file_path:
            raise OSError("Permission denied")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", failing_unlink)

    assert service.recover_pending_deletions() == 0

    chroma.delete_document.assert_called_once_with(
        owner_id=303,
        document_id="doc-file-error",
    )
    assert file_path.exists()
    repository.delete_owned_document.assert_not_called()


def test_recovery_keeps_record_when_registry_deletion_fails(
    recovery_setup,
    monkeypatch,
):
    service, _, repository, chroma, storage = recovery_setup
    document = SimpleNamespace(
        id="doc-db-error",
        owner_id=404,
        stored_filename="doc-db-error_report.pdf",
    )
    repository.list_pending_deletions.return_value = [document]
    repository.claim_pending_deletion.return_value = document
    repository.delete_owned_document.side_effect = RuntimeError("Database unavailable")

    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        lambda db: repository,
    )

    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")

    assert service.recover_pending_deletions() == 0

    chroma.delete_document.assert_called_once_with(
        owner_id=404,
        document_id="doc-db-error",
    )
    assert not file_path.exists()
    repository.delete_owned_document.assert_called_once_with(
        "doc-db-error",
        404,
    )


def test_recovery_continues_after_one_document_fails(
    recovery_setup,
    monkeypatch,
):
    service, _, repository, chroma, storage = recovery_setup
    first = SimpleNamespace(
        id="doc-bad",
        owner_id=101,
        stored_filename="../unsafe.pdf",
    )
    second = SimpleNamespace(
        id="doc-good",
        owner_id=202,
        stored_filename="doc-good.pdf",
    )
    repository.list_pending_deletions.return_value = [first, second]
    repository.claim_pending_deletion.side_effect = [first, second]
    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        lambda db: repository,
    )

    file_path = storage / second.stored_filename
    file_path.write_text("test document", encoding="utf-8")

    assert service.recover_pending_deletions() == 1

    chroma.delete_document.assert_called_once_with(
        owner_id=202,
        document_id="doc-good",
    )
    repository.delete_owned_document.assert_called_once_with("doc-good", 202)
    assert not file_path.exists()


def test_recovery_rejects_invalid_batch_size():
    with pytest.raises(ValueError, match="batch_size"):
        DocumentDeletionRecoveryService(batch_size=0)


def test_recovery_skips_document_claimed_by_another_worker(
    recovery_setup,
    monkeypatch,
):
    service, _, repository, chroma, storage = recovery_setup
    document = SimpleNamespace(
        id="doc-locked",
        owner_id=101,
        stored_filename="doc-locked_report.pdf",
    )
    repository.list_pending_deletions.return_value = [document]

    # None represents a missing document or a row locked by another worker.
    repository.claim_pending_deletion.return_value = None

    monkeypatch.setattr(
        "app.documents.services.deletion_recovery_service.DocumentRepository",
        lambda db: repository,
    )

    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")

    assert service.recover_pending_deletions() == 0

    repository.claim_pending_deletion.assert_called_once_with("doc-locked")
    chroma.delete_document.assert_not_called()
    repository.delete_owned_document.assert_not_called()
    assert file_path.exists()
