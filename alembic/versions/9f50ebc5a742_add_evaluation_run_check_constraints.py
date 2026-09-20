"""add evaluation run check constraints

Revision ID: 9f50ebc5a742
Revises: f49c0dbf4144
Create Date: 2026-09-18

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9f50ebc5a742"
down_revision: Union[str, Sequence[str], None] = "f49c0dbf4144"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add integrity constraints to evaluation runs."""

    op.create_check_constraint(
        "ck_evaluation_runs_status",
        "evaluation_runs",
        "status IN ('queued', 'running', 'completed', 'failed', 'cancelled')",
    )

    op.create_check_constraint(
        "ck_evaluation_runs_retrieval_hit_rate",
        "evaluation_runs",
        "retrieval_hit_rate >= 0.0 AND retrieval_hit_rate <= 1.0",
    )

    op.create_check_constraint(
        "ck_evaluation_runs_groundedness",
        "evaluation_runs",
        "average_groundedness >= 0.0 AND average_groundedness <= 1.0",
    )

    op.create_check_constraint(
        "ck_evaluation_runs_semantic_relevance",
        "evaluation_runs",
        "average_semantic_relevance >= 0.0 AND average_semantic_relevance <= 1.0",
    )

    op.create_check_constraint(
        "ck_evaluation_runs_average_source_count",
        "evaluation_runs",
        "average_source_count >= 0.0",
    )

    op.create_check_constraint(
        "ck_evaluation_runs_overall_pass_rate",
        "evaluation_runs",
        "overall_pass_rate >= 0.0 AND overall_pass_rate <= 1.0",
    )

    op.create_check_constraint(
        "ck_evaluation_runs_total_cases",
        "evaluation_runs",
        "total_cases >= 0",
    )


def downgrade() -> None:
    """Remove evaluation run integrity constraints."""

    op.drop_constraint(
        "ck_evaluation_runs_total_cases",
        "evaluation_runs",
        type_="check",
    )

    op.drop_constraint(
        "ck_evaluation_runs_overall_pass_rate",
        "evaluation_runs",
        type_="check",
    )

    op.drop_constraint(
        "ck_evaluation_runs_average_source_count",
        "evaluation_runs",
        type_="check",
    )

    op.drop_constraint(
        "ck_evaluation_runs_semantic_relevance",
        "evaluation_runs",
        type_="check",
    )

    op.drop_constraint(
        "ck_evaluation_runs_groundedness",
        "evaluation_runs",
        type_="check",
    )

    op.drop_constraint(
        "ck_evaluation_runs_retrieval_hit_rate",
        "evaluation_runs",
        type_="check",
    )

    op.drop_constraint(
        "ck_evaluation_runs_status",
        "evaluation_runs",
        type_="check",
    )
