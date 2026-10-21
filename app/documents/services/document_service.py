from pathlib import Path

from app.documents.chunking.text_chunker import TextChunker
from app.documents.extractors.extractor_factory import ExtractorFactory


class DocumentService:
    def process(
        self,
        file_path: str,
        *,
        owner_id: str | int | None = None,
        document_id: str | None = None,
        source_name: str | None = None,
    ):
        """Extract and chunk a document, attaching access-control metadata.

        ``owner_id`` is stored on every chunk so retrieval can enforce ownership
        using Chroma's metadata filter. ``source_name`` is the user-visible
        filename; it is deliberately separate from the generated storage path.
        The optional arguments preserve compatibility with offline evaluation
        and existing unit tests that process local files directly.
        """
        extractor = ExtractorFactory.get(file_path)
        documents = extractor.extract(file_path)
        chunked_documents = TextChunker().chunk(documents)

        visible_source = source_name or Path(file_path).name
        for index, document in enumerate(chunked_documents):
            document.metadata = dict(document.metadata or {})
            document.metadata["source"] = visible_source
            document.metadata["chunk_id"] = index
            if owner_id is not None:
                document.metadata["owner_id"] = str(owner_id)
            if document_id is not None:
                document.metadata["document_id"] = str(document_id)

        return chunked_documents
