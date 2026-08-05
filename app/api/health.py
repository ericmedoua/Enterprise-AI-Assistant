from fastapi import APIRouter  # type: ignore[import-not-found]
from fastapi import Depends

"""
router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy"}
"""

from app.health.dependencies import (
    get_health_service,
)

from app.health.health_service import (
    HealthService,
)

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/")
def health(
    service: HealthService = Depends(
        get_health_service,
    ),
):

    return service.status()
