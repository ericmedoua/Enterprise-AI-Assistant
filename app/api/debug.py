from fastapi import APIRouter

from app.schemas.debug import RetrievalDebugResponse
from app.services.retrieval_debug_service import RetrievalDebugService

router = APIRouter(
    prefix="/debug",
    tags=["Debug"],
)

service = RetrievalDebugService()


@router.get(
    "/retrieval",
    response_model=RetrievalDebugResponse,
)
def debug_retrieval(
    query: str,
):

    return service.search(query)
