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
