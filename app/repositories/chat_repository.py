from typing import Optional

from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.models.message import Message


class ChatRepository:
    def __init__(self, db: Session):

        self.db = db

    # --------------------------------------------------
    # Chat Session Methods
    # --------------------------------------------------

    def create_session(
        self,
        user_id: int,
        title: str,
    ) -> ChatSession:

        session = ChatSession(
            user_id=user_id,
            title=title,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_session(
        self,
        session_id: int,
    ) -> Optional[ChatSession]:

        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_user_sessions(
        self,
        user_id: int,
    ) -> list[ChatSession]:

        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    def update_title(
        self,
        session: ChatSession,
        new_title: str,
    ) -> ChatSession:

        session.title = new_title

        self.db.commit()

        self.db.refresh(session)

        return session

    def delete_session(
        self,
        session: ChatSession,
    ) -> None:

        self.db.delete(session)

        self.db.commit()

    # --------------------------------------------------
    # Message Methods
    # --------------------------------------------------

    def save_message(
        self,
        session_id: int,
        role: str,
        content: str,
    ) -> Message:

        message = Message(
            session_id=session_id,
            role=role,
            content=content,
        )

        self.db.add(message)

        self.db.commit()

        self.db.refresh(message)

        return message

    def get_messages(
        self,
        session_id: int,
    ) -> list[Message]:

        return (
            self.db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def delete_messages(
        self,
        session_id: int,
    ):

        (self.db.query(Message).filter(Message.session_id == session_id).delete())

        self.db.commit()

    def create_session(
        self,
        user_id: int,
        title: str = "New Chat",
    ):

        session = ChatSession(
            user_id=user_id,
            title=title,
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_sessions(
        self,
        user_id: int,
    ):

        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .all()
        )

    def get_session(
        self,
        session_id: int,
    ):

        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def rename_session(
        self,
        session_id: int,
        title: str,
    ):

        session = self.get_session(session_id)

        if session is None:
            return None

        session.title = title

        self.db.commit()

        self.db.refresh(session)

        return session

    def delete_session(
        self,
        session_id: int,
    ):

        session = self.get_session(session_id)

        if session is None:
            return

        self.db.delete(session)

        self.db.commit()

    def get_summary(
        self,
        session_id: int,
    ):

        session = self.db.get(ChatSession, session_id)

        return session.summary or ""

    def update_summary(
        self,
        session_id: int,
        summary: str,
    ):
        session = self.db.get(
            ChatSession,
            session_id,
        )

        if session is None:
            return

        session.summary = summary

        self.db.commit()

    def get_recent_messages(
        self,
        session_id: int,
        limit: int = 8,
    ):
        messages = (
            self.db.query(Message)
            .filter(
                Message.session_id == session_id
            )
            .order_by(Message.id.desc())
            .limit(limit)
            .all()
        )

        return list(
            reversed(messages)
        )
    def count_messages(
        self,
        session_id: int,
    ) -> int:

        return (
            self.db.query(Message)
            .filter(
                Message.session_id == session_id,
            )
            .count()
        )

    def delete_old_messages(
        self,
        session_id: int,
        keep_last: int = 8,
    ):
        messages = (
            self.db.query(Message)
            .filter(
                Message.session_id == session_id,
            )
            .order_by(Message.id.desc())
            .all()
        )

        old_messages = messages[keep_last:]

        for message in old_messages:
            self.db.delete(message)

        self.db.commit()
