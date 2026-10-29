from unittest.mock import MagicMock

from app.ai.vectorstore.chroma_service import ChromaService


def test_delete_document_filters_by_owner_and_document():
    service = ChromaService.__new__(ChromaService)
    service.vectorstore = MagicMock()

    service.delete_document(owner_id=101, document_id="doc-123")

    service.vectorstore.delete.assert_called_once_with(
        where={
            "$and": [
                {"owner_id": "101"},
                {"document_id": "doc-123"},
            ]
        }
    )


def test_delete_document_does_not_swallow_vectorstore_errors():
    service = ChromaService.__new__(ChromaService)
    service.vectorstore = MagicMock()
    service.vectorstore.delete.side_effect = RuntimeError("Chroma unavailable")

    try:
        service.delete_document(owner_id=101, document_id="doc-123")
    except RuntimeError as exc:
        assert str(exc) == "Chroma unavailable"
    else:
        raise AssertionError("Expected Chroma deletion error to propagate")


def test_reconcile_document_chunks_deletes_only_stale_ids():
    service = ChromaService.__new__(ChromaService)
    service.vectorstore = MagicMock()
    service.vectorstore.get.return_value = {
        "ids": [
            "doc-123-chunk-0",
            "doc-123-chunk-1",
            "doc-123-chunk-2",
        ],
        "metadatas": [{}, {}, {}],
    }

    service.reconcile_document_chunks(
        owner_id=101,
        document_id="doc-123",
        active_chunk_ids=[
            "doc-123-chunk-0",
            "doc-123-chunk-1",
        ],
    )

    service.vectorstore.get.assert_called_once_with(
        where={
            "$and": [
                {"owner_id": "101"},
                {"document_id": "doc-123"},
            ]
        },
        include=["metadatas"],
    )
    service.vectorstore.delete.assert_called_once_with(
        ids=["doc-123-chunk-2"],
    )


def test_reconcile_document_chunks_does_not_delete_when_nothing_is_stale():
    service = ChromaService.__new__(ChromaService)
    service.vectorstore = MagicMock()
    service.vectorstore.get.return_value = {
        "ids": ["doc-123-chunk-0"],
        "metadatas": [{}],
    }

    service.reconcile_document_chunks(
        owner_id=101,
        document_id="doc-123",
        active_chunk_ids=["doc-123-chunk-0"],
    )

    service.vectorstore.delete.assert_not_called()
