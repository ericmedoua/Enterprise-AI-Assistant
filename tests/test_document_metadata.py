from pathlib import Path

from langchain_core.documents import Document

from app.documents.services.document_service import DocumentService


def test_document_chunks_contain_source_metadata(monkeypatch):
    class FakeExtractor:
        def extract(self, file_path):
            return [
                Document(page_content="First page"),
                Document(page_content="Second page"),
            ]

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

    service = DocumentService()

    result = service.process("storage/This_Book_Belongs_To.pdf")

    assert len(result) == 2

    assert result[0].metadata["source"] == "This_Book_Belongs_To.pdf"
    assert result[0].metadata["chunk_id"] == 0

    assert result[1].metadata["source"] == "This_Book_Belongs_To.pdf"
    assert result[1].metadata["chunk_id"] == 1
