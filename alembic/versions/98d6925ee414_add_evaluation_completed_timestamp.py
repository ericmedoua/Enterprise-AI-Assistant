"""add evaluation completed timestamp

Revision ID: 98d6925ee414
Revises: c1f3b7bd3e0e
Create Date: ...

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "98d6925ee414"
down_revision: Union[str, Sequence[str], None] = "c1f3b7bd3e0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add completed_at to evaluation_runs."""

    op.add_column(
        "evaluation_runs",
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove completed_at from evaluation_runs."""

    op.drop_column(
        "evaluation_runs",
        "completed_at",
    )
