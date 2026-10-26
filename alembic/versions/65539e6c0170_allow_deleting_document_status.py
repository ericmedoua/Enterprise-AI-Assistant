"""allow deleting document status

Revision ID: 65539e6c0170
Revises: 85be7952626b
"""

from alembic import op
import sqlalchemy as sa


revision = "65539e6c0170"
down_revision = "85be7952626b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_constraint(
            "ck_documents_status",
            type_="check",
        )
        batch_op.create_check_constraint(
            "ck_documents_status",
            "status IN ('indexing', 'indexed', 'failed', 'deleting')",
        )


def downgrade() -> None:
    # A downgrade cannot retain an in-progress deletion state.
    # Map such records to failed before restoring the old constraint.
    op.execute(
        sa.text(
            "UPDATE documents "
            "SET status = 'failed', "
            "error_message = 'Deletion was interrupted during schema downgrade.' "
            "WHERE status = 'deleting'"
        )
    )

    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_constraint(
            "ck_documents_status",
            type_="check",
        )
        batch_op.create_check_constraint(
            "ck_documents_status",
            "status IN ('indexing', 'indexed', 'failed')",
        )
