from app.documents.services.document_service import DocumentService
from app.ai.retrieval.dependencies import get_chroma_service
from loguru import logger


class IndexingService:
    def index_document(
        self,
        file_path: str,
    ):

        documents = DocumentService().process(
            file_path,
        )

        get_chroma_service().add_documents(
            documents,
        )

        try:
            logger.info(f"Indexing started: {file_path}")
            logger.info(f"Indexing completed: {file_path}")

        except Exception:
            logger.exception(
                "Document indexing failed"
            )
