from functools import lru_cache

from fastapi import Depends

from app.ai.vectorstore.chroma_service import ChromaService
from app.auth.dependencies import get_current_user
from app.models.user import User


@lru_cache
def get_chroma_service():
    return ChromaService()


def get_retriever():
    """Unscoped retriever for offline evaluation/maintenance only.

    Do not inject this into user-facing request handlers. Request handlers must
    use ``get_user_retriever`` so retrieval is filtered by document ownership.
    """
    return get_chroma_service().as_retriever()


def get_user_retriever(current_user: User = Depends(get_current_user)):
    """Return a retriever restricted to documents owned by the current user."""
    return get_chroma_service().as_retriever(
        search_kwargs={
            "k": 4,
            "filter": {"owner_id": str(current_user.id)},
        }
    )
