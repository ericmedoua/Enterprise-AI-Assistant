from sqlalchemy.orm import Session

from app.models.evaluation_run import EvaluationRun

from app.ai.evaluation.stale_evaluation import (
    is_evaluation_stale,
)

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

EVALUATION_ALLOWED_TRANSITIONS = {
    EVALUATION_STATUS_QUEUED: {
        EVALUATION_STATUS_RUNNING,
        EVALUATION_STATUS_CANCELLED,
    },
    EVALUATION_STATUS_RUNNING: {
        EVALUATION_STATUS_COMPLETED,
        EVALUATION_STATUS_FAILED,
    },
    EVALUATION_STATUS_COMPLETED: set(),
    EVALUATION_STATUS_FAILED: set(),
    EVALUATION_STATUS_CANCELLED: set(),
}

EVALUATION_HISTORY_SORT_FIELDS = {
    "created_at": EvaluationRun.created_at,
    "total_cases": EvaluationRun.total_cases,
    "retrieval_hit_rate": EvaluationRun.retrieval_hit_rate,
    "average_groundedness": EvaluationRun.average_groundedness,
    "average_semantic_relevance": EvaluationRun.average_semantic_relevance,
    "overall_pass_rate": EvaluationRun.overall_pass_rate,
}


def _validate_metric_range(
    metric_name: str,
    value: float,
) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{metric_name} must be between 0.0 and 1.0.")


def _validate_non_negative(
    field_name: str,
    value: float | int,
) -> None:
    if value < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0.")


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
        status: str = EVALUATION_STATUS_COMPLETED,
    ) -> EvaluationRun:

        _validate_metric_range(
            "retrieval_hit_rate",
            retrieval_hit_rate,
        )
        _validate_metric_range(
            "average_groundedness",
            average_groundedness,
        )
        _validate_metric_range(
            "average_semantic_relevance",
            average_semantic_relevance,
        )
        _validate_metric_range(
            "overall_pass_rate",
            overall_pass_rate,
        )
        _validate_non_negative(
            "average_source_count",
            average_source_count,
        )

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
        offset: int = 0,
        dataset_name: str | None = None,
        llm_model: str | None = None,
        embedding_model: str | None = None,
        status: str | None = None,
        quality_gate_passed: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[EvaluationRun]:
        if sort_by not in EVALUATION_HISTORY_SORT_FIELDS:
            raise ValueError(f"Unsupported evaluation history sort field: {sort_by}")

        if sort_order not in {"asc", "desc"}:
            raise ValueError(f"Unsupported evaluation history sort order: {sort_order}")

        query = self._build_runs_query(
            dataset_name=dataset_name,
            llm_model=llm_model,
            embedding_model=embedding_model,
            status=status,
            quality_gate_passed=quality_gate_passed,
            created_after=created_after,
            created_before=created_before,
        )

        sort_column = EVALUATION_HISTORY_SORT_FIELDS[sort_by]

        if sort_order == "asc":
            primary_order = sort_column.asc()
        else:
            primary_order = sort_column.desc()

        if sort_by == "created_at":
            order_by_clauses = [
                primary_order,
                EvaluationRun.id.desc(),
            ]
        else:
            order_by_clauses = [
                primary_order,
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            ]

        query = query.order_by(
            *order_by_clauses,
        )

        if offset:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def _build_runs_query(
        self,
        dataset_name: str | None = None,
        llm_model: str | None = None,
        embedding_model: str | None = None,
        status: str | None = None,
        quality_gate_passed: bool | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ):
        query = self.db.query(EvaluationRun)

        if dataset_name is not None:
            query = query.filter(
                EvaluationRun.dataset_name == dataset_name,
            )

        if llm_model is not None:
            query = query.filter(
                EvaluationRun.llm_model == llm_model,
            )

        if embedding_model is not None:
            query = query.filter(
                EvaluationRun.embedding_model == embedding_model,
            )

        if status is not None:
            query = query.filter(
                EvaluationRun.status == status,
            )

        if quality_gate_passed is not None:
            query = query.filter(
                EvaluationRun.quality_gate_passed == quality_gate_passed,
            )

        if created_after is not None:
            query = query.filter(
                EvaluationRun.created_at >= created_after,
            )

        if created_before is not None:
            query = query.filter(
                EvaluationRun.created_at <= created_before,
            )

        return query

    def count_runs(
        self,
        dataset_name: str | None = None,
        llm_model: str | None = None,
        embedding_model: str | None = None,
        status: str | None = None,
        quality_gate_passed: bool | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        query = self._build_runs_query(
            dataset_name=dataset_name,
            llm_model=llm_model,
            embedding_model=embedding_model,
            status=status,
            quality_gate_passed=quality_gate_passed,
            created_after=created_after,
            created_before=created_before,
        )

        return query.count()

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

    def get_previous_compatible_run(
        self,
        current_run: EvaluationRun,
    ) -> EvaluationRun | None:
        return (
            self.db.query(EvaluationRun)
            .filter(
                EvaluationRun.id != current_run.id,
                EvaluationRun.dataset_name == current_run.dataset_name,
                EvaluationRun.llm_model == current_run.llm_model,
                EvaluationRun.embedding_model == current_run.embedding_model,
                EvaluationRun.total_cases == current_run.total_cases,
            )
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

        if run.status != EVALUATION_STATUS_RUNNING:
            raise ValueError("Evaluation results can only be updated for running runs.")

        if status == EVALUATION_STATUS_COMPLETED and total_cases <= 0:
            raise ValueError("total_cases must be greater than 0 for completed runs.")

        _validate_metric_range(
            "retrieval_hit_rate",
            retrieval_hit_rate,
        )
        _validate_metric_range(
            "average_groundedness",
            average_groundedness,
        )
        _validate_metric_range(
            "average_semantic_relevance",
            average_semantic_relevance,
        )
        _validate_metric_range(
            "overall_pass_rate",
            overall_pass_rate,
        )
        _validate_non_negative(
            "average_source_count",
            average_source_count,
        )

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

        allowed_statuses = EVALUATION_ALLOWED_TRANSITIONS.get(
            run.status,
        )

        if allowed_statuses is None:
            raise ValueError(f"Unknown current evaluation status: {run.status}")

        if status not in allowed_statuses:
            raise ValueError(
                f"Invalid evaluation status transition: {run.status} -> {status}"
            )

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

    def get_previous_compatible_run(
        self,
        current_run: EvaluationRun,
    ) -> EvaluationRun | None:
        return (
            self.db.query(EvaluationRun)
            .filter(
                EvaluationRun.id != current_run.id,
                EvaluationRun.dataset_name == current_run.dataset_name,
                EvaluationRun.llm_model == current_run.llm_model,
                EvaluationRun.embedding_model == current_run.embedding_model,
                EvaluationRun.total_cases == current_run.total_cases,
            )
            .order_by(
                EvaluationRun.created_at.desc(),
                EvaluationRun.id.desc(),
            )
            .first()
        )
