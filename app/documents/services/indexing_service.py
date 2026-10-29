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
        """Index a document with stable IDs and reconcile stale chunks."""
        logger.info("Document indexing started: document_id={}", document_id)

        documents = DocumentService().process(
            file_path,
            owner_id=owner_id,
            document_id=document_id,
            source_name=source_name,
        )

        chroma_service = get_chroma_service()

        if document_id is not None:
            for index, document in enumerate(documents):
                document.id = f"{document_id}-chunk-{index}"

        chroma_service.add_documents(documents)

        if documents and owner_id is not None and document_id is not None:
            chroma_service.reconcile_document_chunks(
                owner_id=owner_id,
                document_id=document_id,
                active_chunk_ids=[document.id for document in documents],
            )

        logger.info(
            "Document indexing completed: document_id={}, chunks={}",
            document_id,
            len(documents),
        )
        return len(documents)
