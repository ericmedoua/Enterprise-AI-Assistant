from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService
from app.services.dependencies import get_auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    request: UserRegister,
    service: AuthService = Depends(get_auth_service),
):
    user = service.register(
        username=request.username,
        email=request.email,
        password=request.password,
    )

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    token = service.login(
        request.email,
        request.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
