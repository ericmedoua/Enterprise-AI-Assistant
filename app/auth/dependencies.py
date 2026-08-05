from fastapi import Depends

from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token

from app.auth.security import oauth2_scheme

from app.database.session import get_db

from app.repositories.user_repository import UserRepository

from app.core.exceptions import AppException


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    payload = decode_access_token(token)

    if payload is None:
        raise AppException(
            "Invalid token",
            401,
        )

    user_id = payload["sub"]

    repository = UserRepository(db)

    user = repository.get_by_id(int(user_id))

    if user is None:
        raise AppException(
            "User not found",
            404,
        )

    return user
