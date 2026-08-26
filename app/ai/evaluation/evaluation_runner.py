from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.evaluation.benchmark import (
    run_rag_evaluation_report,
)
from app.ai.evaluation.datasets.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)
from app.ai.evaluation.evaluation_metadata import (
    EvaluationMetadata,
)
from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)
from app.ai.evaluation.evaluation_snapshot_service import (
    build_evaluation_snapshot,
)
from app.ai.evaluation.quality_gate import (
    QualityGateResult,
    evaluate_quality_gate,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)
from app.core.constants import (
    EVALUATION_STATUS_COMPLETED,
    EVALUATION_STATUS_FAILED,
    EVALUATION_STATUS_RUNNING,
    EVALUATION_STATUS_QUEUED,
)

from app.models.evaluation_run import (
    EvaluationRun,
)


@dataclass(frozen=True)
class EvaluationRunResult:
    snapshot: EvaluationSnapshot
    evaluation_run_id: int


class EvaluationRunner:
    def __init__(
        self,
        db: Session,
        metadata: EvaluationMetadata,
    ):
        self.db = db
        self.metadata = metadata
        self.repository = EvaluationRepository(db)

    def run(
        self,
        dataset_name: str = "rag-evaluation-v1",
    ) -> EvaluationRunResult:

        evaluation_run = self.create_run(
        dataset_name
    )

        return self.execute_run(
        evaluation_run.id,
        dataset_name,
    )


    def update_results(
        self,
        run_id: int,
        total_cases: int,
        retrieval_hit_rate: float,
        average_groundedness: float,
        average_semantic_relevance: float,
        average_source_count: float,
        overall_pass_rate: float,
        quality_gate_passed: bool,
        status: str,
    ) -> EvaluationRun | None:
        run = self.db.get(
            EvaluationRun,
            run_id,
        )

        if run is None:
            return None

        run.total_cases = total_cases
        run.retrieval_hit_rate = retrieval_hit_rate
        run.average_groundedness = average_groundedness
        run.average_semantic_relevance = average_semantic_relevance
        run.average_source_count = average_source_count
        run.overall_pass_rate = overall_pass_rate
        run.quality_gate_passed = quality_gate_passed
        run.status = status

        self.db.commit()
        self.db.refresh(run)

        return run

    def create_run(
        self,
        dataset_name: str = "rag-evaluation-v1",
    ):
        return self.repository.create_run(
            dataset_name=dataset_name,
            llm_model=self.metadata.llm_model,
            embedding_model=self.metadata.embedding_model,
            git_commit=self.metadata.git_commit,
            total_cases=0,
            retrieval_hit_rate=0.0,
            average_groundedness=0.0,
            average_semantic_relevance=0.0,
            average_source_count=0.0,
            overall_pass_rate=0.0,
            quality_gate_passed=False,
            status=EVALUATION_STATUS_QUEUED,
        )

    def execute_run(
        self,
        evaluation_run_id: int,
        dataset_name: str = "rag-evaluation-v1",
    ) -> EvaluationRunResult:

        updated_run = self.repository.update_status(
            evaluation_run_id,
            EVALUATION_STATUS_RUNNING,
        )

        if updated_run is None:
            raise RuntimeError(
                "Evaluation run not found."
            )

        try:
            report = run_rag_evaluation_report(
                RAG_EVALUATION_DATASET
            )

            quality_gate = evaluate_quality_gate(
                report
            )

            completed_run = self.repository.update_results(
                run_id=evaluation_run_id,
                total_cases=report.total_cases,
                retrieval_hit_rate=(
                    report.retrieval_hit_rate
                ),
                average_groundedness=(
                    report.average_groundedness
                ),
                average_semantic_relevance=(
                    report.average_semantic_relevance
                ),
                average_source_count=(
                    report.average_source_count
                ),
                overall_pass_rate=(
                    report.overall_pass_rate
                ),
                quality_gate_passed=(
                    quality_gate.passed
                ),
                status=EVALUATION_STATUS_COMPLETED,
            )

            if completed_run is None:
                raise RuntimeError(
                    "Evaluation run disappeared during execution."
                )

            snapshot = build_evaluation_snapshot(
                repository=self.repository,
                dataset_name=dataset_name,
                report=report,
                quality_gate=quality_gate,
                current_run_id=completed_run.id,
            )

            return EvaluationRunResult(
                snapshot=snapshot,
                evaluation_run_id=completed_run.id,
            )

        except Exception:
            self.repository.update_status(
                evaluation_run_id,
                EVALUATION_STATUS_FAILED,
            )
            raise