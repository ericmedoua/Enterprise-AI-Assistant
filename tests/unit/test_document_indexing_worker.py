from unittest.mock import MagicMock

from app.api import documents


def configure_worker_mocks(monkeypatch, *, chunk_count=None, index_error=None):
    indexing_service = MagicMock()

    if index_error is not None:
        indexing_service.index_document.side_effect = index_error
    else:
        indexing_service.index_document.return_value = chunk_count

    monkeypatch.setattr(
        documents,
        "IndexingService",
        lambda: indexing_service,
    )

    db = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = db

    monkeypatch.setattr(
        documents,
        "SessionLocal",
        lambda: session_context,
    )

    repository = MagicMock()
    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        MagicMock(return_value=repository),
    )

    return indexing_service, repository


def test_indexing_worker_persists_indexed_status_and_chunk_count(monkeypatch):
    indexing_service, repository = configure_worker_mocks(
        monkeypatch,
        chunk_count=5,
    )

    result = documents._index_document_to_chroma(
        "storage/example.pdf",
        owner_id=101,
        document_id="document-123",
        source_name="example.pdf",
    )

    assert result == 5

    indexing_service.index_document.assert_called_once_with(
        "storage/example.pdf",
        owner_id=101,
        document_id="document-123",
        source_name="example.pdf",
    )

    repository.update_status.assert_called_once_with(
        "document-123",
        "indexed",
        chunk_count=5,
    )


def test_indexing_worker_cleans_up_vectors_if_indexing_raises(
    monkeypatch,
):
    indexing_service, repository = configure_worker_mocks(
        monkeypatch,
        index_error=RuntimeError("Chroma insertion failed"),
    )

    chroma_service = MagicMock()
    monkeypatch.setattr(
        documents,
        "get_chroma_service",
        lambda: chroma_service,
    )

    result = documents._index_document_to_chroma(
        "storage/example.pdf",
        owner_id=101,
        document_id="document-456",
        source_name="example.pdf",
    )

    assert result is None

    indexing_service.index_document.assert_called_once()
    chroma_service.delete_document.assert_called_once_with(
        owner_id=101,
        document_id="document-456",
    )

    repository.update_status.assert_called_once_with(
        "document-456",
        "failed",
        error_message="Document indexing failed.",
    )


def test_indexing_worker_logs_if_failed_status_cannot_be_saved(monkeypatch):
    configure_worker_mocks(
        monkeypatch,
        index_error=RuntimeError("Indexing error"),
    )

    repository = MagicMock()
    repository.update_status.side_effect = RuntimeError("Database unavailable")

    monkeypatch.setattr(
        documents,
        "DocumentRepository",
        MagicMock(return_value=repository),
    )

    result = documents._index_document_to_chroma(
        "storage/example.pdf",
        owner_id=101,
        document_id="document-789",
        source_name="example.pdf",
    )

    assert result is None
    repository.update_status.assert_called_once_with(
        "document-789",
        "failed",
        error_message="Document indexing failed.",
    )


def test_indexing_worker_cleans_up_vectors_if_indexed_status_fails(
    monkeypatch,
):
    indexing_service, repository = configure_worker_mocks(
        monkeypatch,
        chunk_count=5,
    )

    repository.update_status.side_effect = [
        RuntimeError("Database unavailable"),
        None,
    ]

    chroma_service = MagicMock()
    monkeypatch.setattr(
        documents,
        "get_chroma_service",
        lambda: chroma_service,
    )

    result = documents._index_document_to_chroma(
        "storage/example.pdf",
        owner_id=101,
        document_id="document-999",
        source_name="example.pdf",
    )

    assert result is None

    chroma_service.delete_document.assert_called_once_with(
        owner_id=101,
        document_id="document-999",
    )

    assert repository.update_status.call_count == 2
    repository.update_status.assert_called_with(
        "document-999",
        "failed",
        error_message="Document indexing failed.",
    )


def test_indexing_worker_persists_failed_status_if_vector_cleanup_fails(
    monkeypatch,
):
    _, repository = configure_worker_mocks(
        monkeypatch,
        chunk_count=5,
    )

    repository.update_status.side_effect = [
        RuntimeError("Database unavailable"),
        None,
    ]

    chroma_service = MagicMock()
    chroma_service.delete_document.side_effect = RuntimeError("Chroma unavailable")

    monkeypatch.setattr(
        documents,
        "get_chroma_service",
        lambda: chroma_service,
    )

    result = documents._index_document_to_chroma(
        "storage/example.pdf",
        owner_id=101,
        document_id="document-1000",
        source_name="example.pdf",
    )

    assert result is None

    chroma_service.delete_document.assert_called_once_with(
        owner_id=101,
        document_id="document-1000",
    )

    assert repository.update_status.call_count == 2
    repository.update_status.assert_called_with(
        "document-1000",
        "failed",
        error_message="Document indexing failed.",
    )
