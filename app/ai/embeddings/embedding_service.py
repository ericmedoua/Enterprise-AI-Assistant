from langchain_huggingface import HuggingFaceEmbeddings

from app.ai.cache.embedding_cache import EmbeddingCache
from app.core.config import settings


class EmbeddingService:
    def __init__(
        self,
        cache: EmbeddingCache,
    ):
        self.cache = cache

        self.model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
        )

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        cached = self.cache.get(text)

        if cached is not None:
            return cached

        embedding = self.model.embed_query(text)

        self.cache.put(
            text,
            embedding,
        )

        return embedding

    def embed_documents(
    self,
    texts: list[str],
) -> list[list[float]]:
        embeddings = [None] * len(texts)

        missing: list[str] = []
        missing_indexes: list[int] = []

        for index, text in enumerate(texts):
            cached = self.cache.get(text)

            if cached is not None:
                embeddings[index] = cached
            else:
                missing.append(text)
                missing_indexes.append(index)

        if missing:
            computed = self.model.embed_documents(missing)

            for index, text, embedding in zip(missing_indexes, missing, computed):
                self.cache.put(text, embedding)
                embeddings[index] = embedding

        return embeddings