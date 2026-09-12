"""add evaluation completed timestamp

Revision ID: 98d6925ee414
Revises: c1f3b7bd3e0e
Create Date: ...

"""

from typing import Sequence, Union

from alembic import op


revision: str = "98d6925ee414"
down_revision: Union[str, Sequence[str], None] = "c1f3b7bd3e0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: completed_at is already added by the parent migration."""
    pass


def downgrade() -> None:
    """No-op: completed_at is owned by the parent migration."""
    pass
