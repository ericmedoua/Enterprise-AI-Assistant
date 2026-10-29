from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.ai.embeddings.dependencies import get_embedding_service
from app.core.config import settings


class ChromaService:
    def __init__(self):
        self.embedding_service = get_embedding_service()

        self.vectorstore = Chroma(
            collection_name="enterprise_documents",
            persist_directory=settings.chroma_path,
            embedding_function=self.embedding_service,
        )

    def add_documents(self, documents: list[Document]):
        """Ingest LangChain documents into Chroma."""
        if not documents:
            return
        self.vectorstore.add_documents(documents)

    def delete_document(
        self,
        *,
        owner_id: str | int,
        document_id: str,
    ) -> None:
        """Delete vectors belonging only to the specified owner's document."""
        self.vectorstore.delete(
            where={
                "$and": [
                    {"owner_id": str(owner_id)},
                    {"document_id": str(document_id)},
                ]
            }
        )

    def reconcile_document_chunks(
        self,
        *,
        owner_id: str | int,
        document_id: str,
        active_chunk_ids: list[str],
    ) -> None:
        """Remove obsolete chunks for one owner's successfully indexed document."""
        if not active_chunk_ids:
            return

        existing = self.vectorstore.get(
            where={
                "$and": [
                    {"owner_id": str(owner_id)},
                    {"document_id": str(document_id)},
                ]
            },
            include=["metadatas"],
        )

        active_chunk_id_set = set(active_chunk_ids)

        stale_ids = [
            vector_id
            for vector_id in existing["ids"]
            if vector_id not in active_chunk_id_set
        ]

        if stale_ids:
            self.vectorstore.delete(ids=stale_ids)

    def similarity_search(self, query: str, k: int = 4):
        return self.vectorstore.similarity_search(query, k=k)

    def as_retriever(self, search_kwargs: dict | None = None, **kwargs):
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs, **kwargs)

    def similarity_search_with_score(self, query: str, k: int = 4):
        return self.vectorstore.similarity_search_with_score(query, k=k)
