from app.ai.cache.retriever_cache import (
    RetrieverCache,
)


class CachedRetriever:
    def __init__(
        self,
        retriever,
        cache: RetrieverCache,
    ):

        self.retriever = retriever
        self.cache = cache

    def invoke(
        self,
        question: str,
    ):

        cached = self.cache.get(
            question,
        )

        if cached is not None:
            return cached

        documents = self.retriever.invoke(
            question,
        )

        self.cache.put(
            question,
            documents,
        )

        return documents
