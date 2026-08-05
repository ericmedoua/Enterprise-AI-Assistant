from functools import lru_cache

from app.ai.vectorstore.chroma_service import ChromaService


@lru_cache
def get_chroma_service():
    return ChromaService()


def get_retriever():
    return get_chroma_service().as_retriever()
