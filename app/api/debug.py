from fastapi import APIRouter, Depends

from app.schemas.debug import RetrievalDebugResponse
from app.services.retrieval_debug_service import RetrievalDebugService
from functools import lru_cache


@lru_cache
def get_retrieval_debug_service():
    return RetrievalDebugService()


# router instance for this module
router = APIRouter()


@router.get(
    "/retrieval",
    response_model=RetrievalDebugResponse,
)
def debug_retrieval(
    query: str,
    service: RetrievalDebugService = Depends(get_retrieval_debug_service),
):
    return service.search(query)
