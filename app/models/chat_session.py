from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from sqlalchemy import Text


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    summary = Column(
        Text,
        nullable=True,
        default="",
    )
