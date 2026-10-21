from langchain_core.documents import Document

from app.documents.services.document_service import DocumentService


def test_document_chunks_include_owner_and_document_identity(monkeypatch):
    class FakeExtractor:
        def extract(self, file_path):
            return [Document(page_content="Confidential internal policy")]

    class FakeChunker:
        def chunk(self, documents):
            return documents

    monkeypatch.setattr(
        "app.documents.services.document_service.ExtractorFactory.get",
        lambda file_path: FakeExtractor(),
    )
    monkeypatch.setattr(
        "app.documents.services.document_service.TextChunker",
        lambda: FakeChunker(),
    )

    chunks = DocumentService().process(
        "storage/generated-id.pdf",
        owner_id=42,
        document_id="doc-abc",
        source_name="internal-policy.pdf",
    )

    assert len(chunks) == 1
    assert chunks[0].metadata["owner_id"] == "42"
    assert chunks[0].metadata["document_id"] == "doc-abc"
    assert chunks[0].metadata["source"] == "internal-policy.pdf"
    assert chunks[0].metadata["chunk_id"] == 0


def test_legacy_document_processing_remains_compatible(monkeypatch):
    class FakeExtractor:
        def extract(self, file_path):
            return [Document(page_content="Legacy content")]

    class FakeChunker:
        def chunk(self, documents):
            return documents

    monkeypatch.setattr(
        "app.documents.services.document_service.ExtractorFactory.get",
        lambda file_path: FakeExtractor(),
    )
    monkeypatch.setattr(
        "app.documents.services.document_service.TextChunker",
        lambda: FakeChunker(),
    )

    chunks = DocumentService().process("storage/legacy.pdf")
    assert chunks[0].metadata["source"] == "legacy.pdf"
    assert "owner_id" not in chunks[0].metadata
