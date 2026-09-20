from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.core.constants import EVALUATION_STATUS_COMPLETED


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed', 'cancelled')",
            name="ck_evaluation_runs_status",
        ),
        CheckConstraint(
            "retrieval_hit_rate >= 0.0 AND retrieval_hit_rate <= 1.0",
            name="ck_evaluation_runs_retrieval_hit_rate",
        ),
        CheckConstraint(
            "average_groundedness >= 0.0 AND average_groundedness <= 1.0",
            name="ck_evaluation_runs_groundedness",
        ),
        CheckConstraint(
            "average_semantic_relevance >= 0.0 AND average_semantic_relevance <= 1.0",
            name="ck_evaluation_runs_semantic_relevance",
        ),
        CheckConstraint(
            "average_source_count >= 0.0",
            name="ck_evaluation_runs_average_source_count",
        ),
        CheckConstraint(
            "overall_pass_rate >= 0.0 AND overall_pass_rate <= 1.0",
            name="ck_evaluation_runs_overall_pass_rate",
        ),
        CheckConstraint(
            "total_cases >= 0",
            name="ck_evaluation_runs_total_cases",
        ),
        CheckConstraint(
            "completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at",
            name="ck_evaluation_runs_timestamp_order",
        ),
    )

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
        default=EVALUATION_STATUS_COMPLETED,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
    )


Index(
    "ix_evaluation_runs_created_at_id",
    EvaluationRun.created_at.desc(),
    EvaluationRun.id.desc(),
)

Index(
    "ix_evaluation_runs_compatibility",
    EvaluationRun.dataset_name,
    EvaluationRun.llm_model,
    EvaluationRun.embedding_model,
    EvaluationRun.total_cases,
    EvaluationRun.created_at.desc(),
    EvaluationRun.id.desc(),
)
