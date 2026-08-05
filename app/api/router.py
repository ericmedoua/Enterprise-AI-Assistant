from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.demo import router as demo_router
from app.api.health import router as health_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.debug import router as debug_router

router = APIRouter()

router.include_router(demo_router, tags=["Demo"])
router.include_router(health_router, tags=["Health"])
router.include_router(auth_router)
router.include_router(documents_router)
router.include_router(chat_router)
router.include_router(
    debug_router,
    prefix="/api/v1",
)
