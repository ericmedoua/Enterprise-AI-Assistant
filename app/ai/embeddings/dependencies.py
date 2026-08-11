from app.ai.cache.dependencies import get_embedding_cache
from app.ai.embeddings.embedding_service import EmbeddingService
from functools import lru_cache


@lru_cache
def get_embedding_service():
    return EmbeddingService(get_embedding_cache())
