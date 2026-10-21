from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.repositories.chat_repository import (
    ChatRepository,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)
from app.repositories.document_repository import DocumentRepository


def get_chat_repository(
    db: Session = Depends(get_db),
):

    return ChatRepository(db)


def get_evaluation_repository(
    db: Session = Depends(get_db),
):

    return EvaluationRepository(db)


def get_document_repository(
    db: Session = Depends(get_db),
):
    return DocumentRepository(db)
