from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.ai.embeddings.dependencies import (
    get_embedding_service,
)

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
        """Ingests a list of LangChain Document objects directly into Chroma."""
        if not documents:
            return
        self.vectorstore.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4):
        return self.vectorstore.similarity_search(query, k=k)

    def as_retriever(self, search_kwargs: dict | None = None, **kwargs):
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs, **kwargs)

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
    ):
        return self.vectorstore.similarity_search_with_score(
            query,
            k=k,
        )
