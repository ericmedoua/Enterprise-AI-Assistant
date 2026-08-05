from app.ai.cache.embedding_cache import (
    EmbeddingCache,
)
from app.ai.cache.retriever_cache import (
    RetrieverCache,
)

_embedding_cache = EmbeddingCache()
_retriever_cache = RetrieverCache()


def get_embedding_cache():
    return _embedding_cache


def get_retriever_cache():

    return _retriever_cache
