"""add evaluation experiment metadata

Revision ID: 62a194eb3fd5
Revises: d5bd14c3874a
Create Date: ...

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "62a194eb3fd5"
down_revision: Union[str, Sequence[str], None] = "d5bd14c3874a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add experiment metadata to existing evaluation runs."""

    op.add_column(
        "evaluation_runs",
        sa.Column(
            "llm_model",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "evaluation_runs",
        sa.Column(
            "embedding_model",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "evaluation_runs",
        sa.Column(
            "git_commit",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE evaluation_runs
        SET
            llm_model = 'unknown',
            embedding_model = 'unknown',
            git_commit = 'unknown'
        WHERE
            llm_model IS NULL
            OR embedding_model IS NULL
            OR git_commit IS NULL
        """
    )

    op.alter_column(
        "evaluation_runs",
        "llm_model",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "evaluation_runs",
        "embedding_model",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "evaluation_runs",
        "git_commit",
        existing_type=sa.String(length=64),
        nullable=False,
    )


def downgrade() -> None:
    """Remove experiment metadata."""

    op.drop_column(
        "evaluation_runs",
        "git_commit",
    )

    op.drop_column(
        "evaluation_runs",
        "embedding_model",
    )

    op.drop_column(
        "evaluation_runs",
        "llm_model",
    )
