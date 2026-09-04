from sqlalchemy.orm import Session

from app.models.evaluation_run import EvaluationRun

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)
from datetime import datetime, timezone

from app.core.constants import (
    EVALUATION_STATUS_CANCELLED,
    EVALUATION_STATUS_COMPLETED,
    EVALUATION_STATUS_FAILED,
    EVALUATION_STATUS_QUEUED,
    EVALUATION_STATUS_RUNNING,
)
from app.ai.evaluation.stale_evaluation import (
    is_evaluation_stale,
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
        llm_model: str,
        embedding_model: str,
        git_commit: str,
        total_cases: int,
        retrieval_hit_rate: float,
        average_groundedness: float,
        average_semantic_relevance: float,
        average_source_count: float,
        overall_pass_rate: float,
        quality_gate_passed: bool,
        status: str = "completed",
    ) -> EvaluationRun:

        evaluation_run = EvaluationRun(
            dataset_name=dataset_name,
            llm_model=llm_model,
            embedding_model=embedding_model,
            git_commit=git_commit,
            total_cases=total_cases,
            retrieval_hit_rate=retrieval_hit_rate,
            average_groundedness=average_groundedness,
            average_semantic_relevance=average_semantic_relevance,
            average_source_count=average_source_count,
            overall_pass_rate=overall_pass_rate,
            quality_gate_passed=quality_gate_passed,
            status=status,
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
        limit: int | None = None,
    ) -> list[EvaluationRun]:
        query = (
            self.db.query(EvaluationRun)
            .order_by(
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            )
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def create_run_from_report(
        self,
        dataset_name: str,
        llm_model: str,
        embedding_model: str,
        git_commit: str,
        report: EvaluationReport,
        quality_gate: QualityGateResult,
    ) -> EvaluationRun:

        return self.create_run(
            dataset_name=dataset_name,
            llm_model=llm_model,
            embedding_model=embedding_model,
            git_commit=git_commit,
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

    def list_runs_by_dataset(
        self,
        dataset_name: str,
    ) -> list[EvaluationRun]:
        return (
            self.db.query(EvaluationRun)
            .filter(
                EvaluationRun.dataset_name == dataset_name,
            )
            .order_by(
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            )
            .all()
        )

    def list_runs_by_model(
        self,
        llm_model: str,
        embedding_model: str,
    ) -> list[EvaluationRun]:
        return (
            self.db.query(EvaluationRun)
            .filter(
                EvaluationRun.llm_model == llm_model,
                EvaluationRun.embedding_model == embedding_model,
            )
            .order_by(
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            )
            .all()
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

        if status in {
            EVALUATION_STATUS_COMPLETED,
            EVALUATION_STATUS_FAILED,
        }:
            run.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(run)

        return run

    def update_status(
        self,
        run_id: int,
        status: str,
    ) -> EvaluationRun | None:
        run = self.db.get(
            EvaluationRun,
            run_id,
        )

        if run is None:
            return None

        now = datetime.now(timezone.utc)

        run.status = status

        if status == EVALUATION_STATUS_RUNNING:
            run.started_at = now

        elif status in {
            EVALUATION_STATUS_COMPLETED,
            EVALUATION_STATUS_FAILED,
        }:
            run.completed_at = now

        self.db.commit()
        self.db.refresh(run)

        return run

    def list_running_runs(self) -> list[EvaluationRun]:
        return (
            self.db.query(EvaluationRun)
            .filter(EvaluationRun.status == EVALUATION_STATUS_RUNNING)
            .order_by(EvaluationRun.started_at.asc())
            .all()
        )

    def fail_stale_run(
        self,
        run_id: int,
        timeout_seconds: int = 300,
    ) -> EvaluationRun | None:
        run = self.db.get(
            EvaluationRun,
            run_id,
        )

        if run is None:
            return None

        if not is_evaluation_stale(
            status=run.status,
            started_at=run.started_at,
            timeout_seconds=timeout_seconds,
        ):
            return None

        run.status = EVALUATION_STATUS_FAILED
        run.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(run)

        return run

    def cancel_queued_run(
        self,
        run_id: int,
    ) -> EvaluationRun | None:
        run = self.db.get(
            EvaluationRun,
            run_id,
        )

        if run is None:
            return None

        if run.status != EVALUATION_STATUS_QUEUED:
            return None

        run.status = EVALUATION_STATUS_CANCELLED
        run.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(run)

        return run

    def count_cancelled_runs(self) -> int:
        return (
            self.db.query(EvaluationRun)
            .filter(EvaluationRun.status == EVALUATION_STATUS_CANCELLED)
            .count()
        )
