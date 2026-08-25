"""add evaluation run status

Revision ID: 4350c33ab32c
Revises: 62a194eb3fd5
Create Date: 2026-08-25

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4350c33ab32c"
down_revision: Union[str, Sequence[str], None] = "62a194eb3fd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add evaluation run status."""

    # Existing rows need a value before the column
    # can become NOT NULL.
    op.add_column(
        "evaluation_runs",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE evaluation_runs
        SET status = 'completed'
        WHERE status IS NULL
        """
    )

    op.alter_column(
        "evaluation_runs",
        "status",
        existing_type=sa.String(length=20),
        nullable=False,
    )


def downgrade() -> None:
    """Remove evaluation run status."""

    op.drop_column(
        "evaluation_runs",
        "status",
    )
