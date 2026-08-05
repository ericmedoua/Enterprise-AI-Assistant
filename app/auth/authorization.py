from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user

from app.core.exceptions import AppException


router = APIRouter()


def require_admin(
    current_user=Depends(get_current_user),
):

    if current_user.role != "admin":
        raise AppException(
            "Administrator privileges required.",
            403,
        )

    return current_user

@router.get("/admin")
def admin_dashboard(

    admin=Depends(require_admin),

):

    return {
        "message": "Welcome Admin"
    }
