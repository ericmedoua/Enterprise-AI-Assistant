from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.auth.authorization import require_admin
from app.repositories.dependencies import get_document_repository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentHealthResponse


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/document-health",
    response_model=DocumentHealthResponse,
)
def get_document_health(
    repository: DocumentRepository = Depends(get_document_repository),
):
    metrics = repository.get_document_health_metrics()

    return DocumentHealthResponse(
        **metrics,
        generated_at=datetime.now(timezone.utc),
    )
