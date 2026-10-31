"""add document deletion retry scheduling

Revision ID: 0635b049d064
Revises: 65539e6c0170
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0635b049d064"
down_revision: Union[str, Sequence[str], None] = "65539e6c0170"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.add_column(
            sa.Column(
                "deletion_attempts",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("0"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "deletion_next_retry_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )

    # Remove the server default after existing rows have been initialized.
    with op.batch_alter_table("documents") as batch_op:
        batch_op.alter_column(
            "deletion_attempts",
            server_default=None,
        )


def downgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_column("deletion_next_retry_at")
        batch_op.drop_column("deletion_attempts")
