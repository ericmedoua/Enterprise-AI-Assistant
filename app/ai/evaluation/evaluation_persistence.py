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
    llm_model: str,
    embedding_model: str,
    git_commit: str,
    report: EvaluationReport,
    quality_gate: QualityGateResult,
):
    repository = EvaluationRepository(db)

    return repository.create_from_evaluation(
        dataset_name=dataset_name,
        llm_model=llm_model,
        embedding_model=embedding_model,
        git_commit=git_commit,
        report=report,
        quality_gate=quality_gate,
    )
