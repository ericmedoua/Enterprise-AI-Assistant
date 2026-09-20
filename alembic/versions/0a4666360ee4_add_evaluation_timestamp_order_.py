"""add evaluation timestamp order constraint

Revision ID: 0a4666360ee4
Revises: 9f50ebc5a742
Create Date: 2026-09-18

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0a4666360ee4"
down_revision: Union[str, Sequence[str], None] = "9f50ebc5a742"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure evaluation completion does not precede evaluation start."""

    op.create_check_constraint(
        "ck_evaluation_runs_timestamp_order",
        "evaluation_runs",
        "completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at",
    )


def downgrade() -> None:
    """Remove the evaluation timestamp-order constraint."""

    op.drop_constraint(
        "ck_evaluation_runs_timestamp_order",
        "evaluation_runs",
        type_="check",
    )
