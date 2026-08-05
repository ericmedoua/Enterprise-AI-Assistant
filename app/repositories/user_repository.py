from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):

        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str):

        return self.db.query(User).filter(User.username == username).first()

    def create(
        self,
        username: str,
        email: str,
        password_hash: str,
    ):

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user

    def get_by_id(self, user_id: int):

        return (
        self.db.query(User)
        .filter(User.id == user_id)
        .first()
    )