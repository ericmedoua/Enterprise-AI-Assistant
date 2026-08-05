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

        return chunked_documents
