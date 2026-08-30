from app.ai.evaluation.evaluation_remediation import (
    remediate_stale_evaluations,
)
from app.core.logger import app_logger
from app.database.session import SessionLocal


def run_stale_evaluation_remediation() -> list[int]:
    """
    Run one stale-evaluation remediation cycle.
    """

    db = SessionLocal()

    try:
        from app.repositories.evaluation_repository import (
            EvaluationRepository,
        )

        repository = EvaluationRepository(db)

        remediated_ids = remediate_stale_evaluations(
            repository=repository,
        )

        if remediated_ids:
            app_logger.warning(f"Remediated stale evaluation runs: {remediated_ids}")
        else:
            app_logger.info("No stale evaluation runs found.")

        return remediated_ids

    finally:
        db.close()
