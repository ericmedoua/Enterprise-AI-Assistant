from pathlib import Path

from app.documents.chunking.text_chunker import TextChunker
from app.documents.extractors.extractor_factory import ExtractorFactory


class DocumentService:
    def process(
        self,
        file_path: str,
    ):
        extractor = ExtractorFactory.get(file_path)

        documents = extractor.extract(file_path)

        chunker = TextChunker()

        chunked_documents = chunker.chunk(documents)

        source_filename = Path(file_path).name

        for index, document in enumerate(chunked_documents):
            document.metadata = document.metadata or {}

            document.metadata["source"] = source_filename
            document.metadata["chunk_id"] = index

        return chunked_documents
