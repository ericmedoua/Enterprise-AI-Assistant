from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    dataset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    llm_model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    embedding_model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    git_commit: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    total_cases: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    retrieval_hit_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    average_groundedness: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    average_semantic_relevance: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    average_source_count: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    overall_pass_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    quality_gate_passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="completed",
    )
