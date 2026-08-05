from app.auth.hashing import hash_password
from app.auth.hashing import verify_password
from app.auth.jwt import create_access_token

from app.core.exceptions import AppException

from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ):

        if self.repository.get_by_email(email):
            raise AppException(
                "Email already exists.",
                409,
            )

        if self.repository.get_by_username(username):
            raise AppException(
                "Username already exists.",
                409,
            )

        return self.repository.create(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

    def login(
        self,
        email: str,
        password: str,
    ):

        user = self.repository.get_by_email(email)

        if user is None:
            raise AppException(
                "Invalid email or password.",
                401,
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise AppException(
                "Invalid email or password.",
                401,
            )

        token = create_access_token(subject=str(user.id))

        return token
