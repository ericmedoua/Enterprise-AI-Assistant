from loguru import logger

from app.ai.retrieval.dependencies import get_chroma_service
from app.documents.services.document_service import DocumentService


class IndexingService:
    def index_document(
        self,
        file_path: str,
        *,
        owner_id: str | int | None = None,
        document_id: str | None = None,
        source_name: str | None = None,
    ) -> int:
        """Index one document and return the number of chunks written."""
        logger.info("Document indexing started: document_id={}", document_id)
        documents = DocumentService().process(
            file_path,
            owner_id=owner_id,
            document_id=document_id,
            source_name=source_name,
        )
        get_chroma_service().add_documents(documents)
        logger.info(
            "Document indexing completed: document_id={}, chunks={}",
            document_id,
            len(documents),
        )
        return len(documents)
