from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.repositories.chat_repository import (
    ChatRepository,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def get_chat_repository(
    db: Session = Depends(get_db),
):

    return ChatRepository(db)


def get_evaluation_repository(
    db: Session = Depends(get_db),
):

    return EvaluationRepository(db)
