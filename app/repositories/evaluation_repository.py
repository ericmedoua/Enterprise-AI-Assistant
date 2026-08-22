from sqlalchemy.orm import Session

from app.models.evaluation_run import EvaluationRun

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


class EvaluationRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_run(
        self,
        dataset_name: str,
        total_cases: int,
        retrieval_hit_rate: float,
        average_groundedness: float,
        average_semantic_relevance: float,
        average_source_count: float,
        overall_pass_rate: float,
        quality_gate_passed: bool,
    ) -> EvaluationRun:

        evaluation_run = EvaluationRun(
            dataset_name=dataset_name,
            total_cases=total_cases,
            retrieval_hit_rate=retrieval_hit_rate,
            average_groundedness=average_groundedness,
            average_semantic_relevance=average_semantic_relevance,
            average_source_count=average_source_count,
            overall_pass_rate=overall_pass_rate,
            quality_gate_passed=quality_gate_passed,
        )

        self.db.add(evaluation_run)
        self.db.commit()
        self.db.refresh(evaluation_run)

        return evaluation_run

    def get_run(
        self,
        run_id: int,
    ) -> EvaluationRun | None:

        return self.db.get(
            EvaluationRun,
            run_id,
        )

    def list_runs(
        self,
    ) -> list[EvaluationRun]:

        return (
            self.db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
        )

    def create_from_evaluation(
        self,
        dataset_name: str,
        report: EvaluationReport,
        quality_gate: QualityGateResult,
    ) -> EvaluationRun:

        return self.create_run(
            dataset_name=dataset_name,
            total_cases=report.total_cases,
            retrieval_hit_rate=report.retrieval_hit_rate,
            average_groundedness=report.average_groundedness,
            average_semantic_relevance=(report.average_semantic_relevance),
            average_source_count=(report.average_source_count),
            overall_pass_rate=(report.overall_pass_rate),
            quality_gate_passed=quality_gate.passed,
        )

    def get_latest_run(
        self,
    ) -> EvaluationRun | None:
        return (
            self.db.query(EvaluationRun)
            .order_by(
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            )
            .first()
        )

    def get_previous_run(
        self,
        current_run_id: int,
    ) -> EvaluationRun | None:
        return (
            self.db.query(EvaluationRun)
            .filter(EvaluationRun.id != current_run_id)
            .order_by(
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            )
            .first()
        )
