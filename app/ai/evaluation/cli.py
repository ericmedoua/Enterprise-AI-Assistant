from app.ai.evaluation.benchmark import (
    run_rag_evaluation_report,
)
from app.ai.evaluation.datasets.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)
from app.ai.evaluation.evaluation_metadata import (
    get_evaluation_metadata,
)
from app.ai.evaluation.evaluation_snapshot_report import (
    format_evaluation_snapshot,
)
from app.ai.evaluation.evaluation_snapshot_service import (
    build_evaluation_snapshot,
)
from app.ai.evaluation.quality_gate import (
    evaluate_quality_gate,
)
from app.database.session import SessionLocal
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def main() -> None:
    report = run_rag_evaluation_report(RAG_EVALUATION_DATASET)

    quality_gate = evaluate_quality_gate(report)

    metadata = get_evaluation_metadata()

    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        current_run = repository.create_from_evaluation(
            dataset_name="rag-evaluation-v1",
            llm_model=metadata.llm_model,
            embedding_model=metadata.embedding_model,
            git_commit=metadata.git_commit,
            report=report,
            quality_gate=quality_gate,
        )

        snapshot = build_evaluation_snapshot(
            repository=repository,
            dataset_name="rag-evaluation-v1",
            report=report,
            quality_gate=quality_gate,
            current_run_id=current_run.id,
        )

        print(format_evaluation_snapshot(snapshot))

    finally:
        db.close()


if __name__ == "__main__":
    main()
