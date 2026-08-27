"""add evaluation lifecycle timestamps

Revision ID: c1f3b7bd3e0e
Revises: 4350c33ab32c
Create Date: 2026-08-26 11:19:19.514091

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1f3b7bd3e0e"
down_revision: Union[str, Sequence[str], None] = "4350c33ab32c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add evaluation lifecycle timestamps."""

    op.add_column(
        "evaluation_runs",
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "evaluation_runs",
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove evaluation lifecycle timestamps."""

    op.drop_column(
        "evaluation_runs",
        "completed_at",
    )

    op.drop_column(
        "evaluation_runs",
        "started_at",
    )
