from sqlalchemy.orm import Session

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def persist_evaluation(
    db: Session,
    dataset_name: str,
    report: EvaluationReport,
    quality_gate: QualityGateResult,
):
    repository = EvaluationRepository(db)

    return repository.create_from_evaluation(
        dataset_name=dataset_name,
        report=report,
        quality_gate=quality_gate,
    )
