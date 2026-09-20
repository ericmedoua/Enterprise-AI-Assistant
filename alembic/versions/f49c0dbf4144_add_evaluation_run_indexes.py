"""add evaluation run indexes

Revision ID: f49c0dbf4144
Revises: 98d6925ee414
Create Date: 2026-09-15

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f49c0dbf4144"
down_revision: Union[str, Sequence[str], None] = "98d6925ee414"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes supporting evaluation history and compatibility queries."""

    op.create_index(
        "ix_evaluation_runs_created_at_id",
        "evaluation_runs",
        ["created_at", "id"],
        postgresql_ops={
            "created_at": "DESC",
            "id": "DESC",
        },
    )

    op.create_index(
        "ix_evaluation_runs_compatibility",
        "evaluation_runs",
        [
            "dataset_name",
            "llm_model",
            "embedding_model",
            "total_cases",
            "created_at",
            "id",
        ],
        postgresql_ops={
            "created_at": "DESC",
            "id": "DESC",
        },
    )


def downgrade() -> None:
    """Remove evaluation history and compatibility indexes."""

    op.drop_index(
        "ix_evaluation_runs_compatibility",
        table_name="evaluation_runs",
    )

    op.drop_index(
        "ix_evaluation_runs_created_at_id",
        table_name="evaluation_runs",
    )
