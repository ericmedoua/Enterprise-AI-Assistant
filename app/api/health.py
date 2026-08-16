from fastapi import APIRouter

from app.health.dependencies import get_health_service


router = APIRouter(
    tags=["Health"],
)


@router.get("/health/", include_in_schema=True)
def health():
    health_service = get_health_service()

    return health_service.status()
