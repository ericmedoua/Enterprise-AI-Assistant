from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from app.documents.services.indexing_service import IndexingService


def test_index_document_assigns_stable_chunk_ids():
    documents = [
        Document(page_content="First chunk", metadata={"chunk_id": 0}),
        Document(page_content="Second chunk", metadata={"chunk_id": 1}),
    ]
    chroma_service = MagicMock()

    with (
        patch(
            "app.documents.services.indexing_service.DocumentService"
        ) as document_service_class,
        patch(
            "app.documents.services.indexing_service.get_chroma_service",
            return_value=chroma_service,
        ),
    ):
        document_service_class.return_value.process.return_value = documents

        count = IndexingService().index_document(
            "document.txt",
            owner_id=101,
            document_id="doc-123",
            source_name="document.txt",
        )

    assert count == 2
    passed_documents = chroma_service.add_documents.call_args.args[0]
    assert [document.id for document in passed_documents] == [
        "doc-123-chunk-0",
        "doc-123-chunk-1",
    ]


def test_index_document_preserves_legacy_behavior_without_document_id():
    documents = [Document(page_content="Legacy chunk")]
    chroma_service = MagicMock()

    with (
        patch(
            "app.documents.services.indexing_service.DocumentService"
        ) as document_service_class,
        patch(
            "app.documents.services.indexing_service.get_chroma_service",
            return_value=chroma_service,
        ),
    ):
        document_service_class.return_value.process.return_value = documents

        count = IndexingService().index_document("legacy.txt")

    assert count == 1
    chroma_service.add_documents.assert_called_once_with(documents)
    assert documents[0].id is None


def test_index_document_reconciles_stale_chunks_after_upsert():
    documents = [
        Document(page_content="Updated chunk", metadata={"chunk_id": 0}),
    ]
    chroma_service = MagicMock()

    with (
        patch(
            "app.documents.services.indexing_service.DocumentService"
        ) as document_service_class,
        patch(
            "app.documents.services.indexing_service.get_chroma_service",
            return_value=chroma_service,
        ),
    ):
        document_service_class.return_value.process.return_value = documents

        count = IndexingService().index_document(
            "document.txt",
            owner_id=101,
            document_id="doc-123",
        )

    assert count == 1
    chroma_service.add_documents.assert_called_once_with(documents)
    chroma_service.reconcile_document_chunks.assert_called_once_with(
        owner_id=101,
        document_id="doc-123",
        active_chunk_ids=["doc-123-chunk-0"],
    )

    assert chroma_service.method_calls[0][0] == "add_documents"
    assert chroma_service.method_calls[1][0] == "reconcile_document_chunks"


def test_index_document_skips_reconciliation_when_no_chunks_are_produced():
    chroma_service = MagicMock()

    with (
        patch(
            "app.documents.services.indexing_service.DocumentService"
        ) as document_service_class,
        patch(
            "app.documents.services.indexing_service.get_chroma_service",
            return_value=chroma_service,
        ),
    ):
        document_service_class.return_value.process.return_value = []

        count = IndexingService().index_document(
            "document.txt",
            owner_id=101,
            document_id="doc-123",
        )

    assert count == 0
    chroma_service.add_documents.assert_called_once_with([])
    chroma_service.reconcile_document_chunks.assert_not_called()
