from fastapi import APIRouter

from app.core.exceptions import AppException

router = APIRouter()


@router.get("/demo-error")
def demo_error():
    raise AppException(
        message="This is a custom exception.",
        status_code=400,
    )
