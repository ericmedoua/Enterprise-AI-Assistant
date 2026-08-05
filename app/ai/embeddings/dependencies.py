from app.ai.cache.dependencies import get_embedding_cache
from app.ai.embeddings.embedding_service import EmbeddingService

_embedding_service = EmbeddingService(
    get_embedding_cache(),
)


def get_embedding_service():

    return _embedding_service
