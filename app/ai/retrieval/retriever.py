from app.ai.embeddings.embedding_service import (
    EmbeddingService,
)

from app.ai.vectorstore.chroma_service import (
    ChromaService,
)


class Retriever:
    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.vector_db = ChromaService()

    def retrieve(
        self,
        question: str,
    ):

        embedding = self.embedding_service.embed(question)

        return self.vector_db.search(embedding)
