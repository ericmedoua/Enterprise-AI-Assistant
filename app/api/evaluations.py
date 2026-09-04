from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.schemas.evaluation import (
    EvaluationHistoryResponse,
    EvaluationObservabilityResponse,
    EvaluationRunResponse,
    EvaluationSnapshotResponse,
    EvaluationMetricTrendResponse,
    EvaluationTrendResponse,
    StaleEvaluationRunResponse,
    StaleEvaluationRunsResponse,
    EvaluationHistoricalTrendResponse,
    EvaluationHistoricalTrendsResponse,
    EvaluationMetricPointResponse,
)
from app.ai.evaluation.evaluation_comparator import (
    compare_evaluation_runs,
)

from app.schemas.evaluation import (
    EvaluationComparisonResponse,
)
from app.ai.evaluation.evaluation_snapshot_service import (
    build_evaluation_snapshot,
)

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)
from app.schemas.evaluation import (
    EvaluationDashboardResponse,
)
from app.ai.evaluation.evaluation_metadata import (
    get_evaluation_metadata,
)

from app.ai.evaluation.evaluation_runner import (
    EvaluationRunner,
)

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)

from app.schemas.evaluation import (
    EvaluationRunStartResponse,
    EvaluationQualityHealthResponse,
    EvaluationHealthResponse,
)
from app.core.constants import (
    EVALUATION_STATUS_QUEUED,
)
from app.database.session import (
    SessionLocal,
)
from app.core.logger import app_logger
from app.ai.evaluation.evaluation_duration import (
    calculate_duration_seconds,
)
from app.ai.evaluation.evaluation_health import (
    evaluate_health,
)

from app.schemas.evaluation import (
    EvaluationHealthResponse,
)

from app.ai.evaluation.evaluation_duration import (
    calculate_duration_seconds,
)

from app.ai.evaluation.stale_evaluation import (
    is_evaluation_stale,
)

from datetime import datetime, timezone

from app.ai.evaluation.evaluation_history import (
    build_evaluation_history,
)

from app.ai.evaluation.evaluation_trend_service import (
    build_latest_evaluation_trends,
)
from app.ai.evaluation.evaluation_historical_trend_service import (
    build_evaluation_historical_trends,
)
from app.ai.evaluation.evaluation_quality_health_service import (
    build_evaluation_quality_health,
)
from app.ai.evaluation.evaluation_health import (
    evaluate_health,
)
from app.ai.evaluation.evaluation_dashboard_service import (
    build_evaluation_dashboard,
)


router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"],
)


def _to_response(run):
    return EvaluationRunResponse(
        id=run.id,
        created_at=run.created_at,
        dataset_name=run.dataset_name,
        llm_model=run.llm_model,
        embedding_model=run.embedding_model,
        git_commit=run.git_commit,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        duration_seconds=calculate_duration_seconds(
            run.started_at,
            run.completed_at,
        ),
        total_cases=run.total_cases,
        retrieval_hit_rate=run.retrieval_hit_rate,
        average_groundedness=run.average_groundedness,
        average_semantic_relevance=(run.average_semantic_relevance),
        average_source_count=run.average_source_count,
        overall_pass_rate=run.overall_pass_rate,
        quality_gate_passed=run.quality_gate_passed,
    )


def _execute_evaluation_in_background(
    evaluation_run_id: int,
) -> None:
    db = SessionLocal()

    try:
        metadata = get_evaluation_metadata()

        runner = EvaluationRunner(
            db=db,
            metadata=metadata,
        )

        runner.execute_run(evaluation_run_id)

    except Exception:
        # EvaluationRunner is responsible for marking
        # the run as FAILED. The background task must
        # not propagate the exception back into the
        # already-completed HTTP response.
        app_logger.exception(f"Evaluation run failed | run_id={evaluation_run_id}")

    finally:
        db.close()


@router.get(
    "/latest",
    response_model=EvaluationRunResponse,
)
def get_latest_evaluation(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    run = repository.get_latest_run()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="No evaluation runs found.",
        )

    return _to_response(run)


@router.get(
    "/history",
    response_model=EvaluationHistoryResponse,
)
def get_evaluation_history(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    runs = repository.list_runs()

    return EvaluationHistoryResponse(runs=[_to_response(run) for run in runs])


@router.get(
    "/dashboard",
    response_model=EvaluationDashboardResponse,
)
def get_evaluation_dashboard(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    try:
        dashboard = build_evaluation_dashboard(repository)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return EvaluationDashboardResponse(
        latest=_to_response(dashboard.latest),
        comparison=(
            EvaluationComparisonResponse(
                retrieval_hit_rate_delta=(
                    dashboard.comparison.retrieval_hit_rate_delta
                ),
                groundedness_delta=(dashboard.comparison.groundedness_delta),
                semantic_relevance_delta=(
                    dashboard.comparison.semantic_relevance_delta
                ),
                source_count_delta=(dashboard.comparison.source_count_delta),
                overall_pass_rate_delta=(dashboard.comparison.overall_pass_rate_delta),
            )
            if dashboard.comparison is not None
            else None
        ),
        quality_health=EvaluationQualityHealthResponse(
            healthy=dashboard.quality_health.healthy,
            status=dashboard.quality_health.status,
            latest_run_id=dashboard.quality_health.latest_run_id,
            quality_gate_passed=(dashboard.quality_health.quality_gate_passed),
            trend_status=dashboard.quality_health.trend_status,
        ),
        operational_health=EvaluationHealthResponse(
            healthy=dashboard.operational_health.healthy,
            running_count=(dashboard.operational_health.running_count),
            stale_count=(dashboard.operational_health.stale_count),
            cancelled_count=(dashboard.operational_health.cancelled_count),
        ),
    )


@router.get(
    "/health",
    response_model=EvaluationHealthResponse,
)
def get_evaluation_health(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    running_runs = repository.list_running_runs()

    cancelled_count = repository.count_cancelled_runs()

    health = evaluate_health(
        running_runs,
        cancelled_count=cancelled_count,
    )

    return EvaluationHealthResponse(
        healthy=health.healthy,
        running_count=health.running_count,
        stale_count=health.stale_count,
        cancelled_count=health.cancelled_count,
    )


@router.get(
    "/stale",
    response_model=StaleEvaluationRunsResponse,
)
def get_stale_evaluations(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    running_runs = repository.list_running_runs()

    stale_runs = []

    for run in running_runs:
        if not is_evaluation_stale(
            status=run.status,
            started_at=run.started_at,
        ):
            continue

        duration = (datetime.now(timezone.utc) - run.started_at).total_seconds()

        # A stale run must have started_at, and its
        # duration is therefore available up to "now".
        if duration is None:
            continue

        stale_runs.append(
            StaleEvaluationRunResponse(
                id=run.id,
                dataset_name=run.dataset_name,
                status=run.status,
                started_at=run.started_at,
                duration_seconds=duration,
            )
        )

    return StaleEvaluationRunsResponse(
        runs=stale_runs,
    )


@router.get(
    "/observability/latest",
    response_model=EvaluationObservabilityResponse,
)
def get_latest_evaluation_observability(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    run = repository.get_latest_run()

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="No evaluation runs found.",
        )

    return EvaluationObservabilityResponse(
        event="rag_evaluation_completed",
        dataset=run.dataset_name,
        total_cases=run.total_cases,
        retrieval_hit_rate=run.retrieval_hit_rate,
        average_groundedness=run.average_groundedness,
        average_semantic_relevance=(run.average_semantic_relevance),
        average_source_count=run.average_source_count,
        overall_pass_rate=run.overall_pass_rate,
        quality_gate_passed=run.quality_gate_passed,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        duration_seconds=calculate_duration_seconds(
            run.started_at,
            run.completed_at,
        ),
    )


@router.get(
    "/observability/history",
    response_model=EvaluationHistoryResponse,
)
def get_evaluation_observability_history(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    runs = repository.list_runs()

    return build_evaluation_history(runs)


@router.get(
    "/trends",
    response_model=EvaluationTrendResponse,
)
def get_evaluation_trends(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    trends = build_latest_evaluation_trends(repository)

    return EvaluationTrendResponse(
        trends=[
            EvaluationMetricTrendResponse(
                metric_name=trend.metric_name,
                previous_value=trend.previous_value,
                current_value=trend.current_value,
                delta=trend.delta,
                direction=trend.direction,
            )
            for trend in trends
        ],
    )


@router.get(
    "/historical-trends",
    response_model=EvaluationHistoricalTrendsResponse,
)
def get_evaluation_historical_trends(
    limit: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    trends = build_evaluation_historical_trends(
        repository,
        limit=limit,
    )

    return EvaluationHistoricalTrendsResponse(
        trends=[
            EvaluationHistoricalTrendResponse(
                metric_name=trend.metric_name,
                direction=trend.direction,
                points=[
                    EvaluationMetricPointResponse(
                        run_id=point.run_id,
                        created_at=point.created_at,
                        value=point.value,
                    )
                    for point in trend.points
                ],
            )
            for trend in trends
        ]
    )


@router.get(
    "/quality-health",
    response_model=EvaluationQualityHealthResponse,
)
def get_evaluation_quality_health(
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    health = build_evaluation_quality_health(repository)

    return EvaluationQualityHealthResponse(
        healthy=health.healthy,
        status=health.status,
        latest_run_id=health.latest_run_id,
        quality_gate_passed=health.quality_gate_passed,
        trend_status=health.trend_status,
    )


@router.post(
    "/{run_id}/fail",
    response_model=EvaluationRunResponse,
)
def fail_stale_evaluation(
    run_id: int,
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    run = repository.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    updated_run = repository.fail_stale_run(
        run_id=run_id,
    )

    if updated_run is None:
        raise HTTPException(
            status_code=409,
            detail=("Evaluation run is not stale or cannot be remediated."),
        )

    return _to_response(updated_run)


@router.post(
    "/{run_id}/cancel",
    response_model=EvaluationRunResponse,
)
def cancel_evaluation_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    run = repository.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    cancelled_run = repository.cancel_queued_run(
        run_id=run_id,
    )

    if cancelled_run is None:
        raise HTTPException(
            status_code=409,
            detail=("Evaluation run cannot be cancelled because it is not queued."),
        )

    return _to_response(cancelled_run)


@router.get(
    "/{run_id}",
    response_model=EvaluationRunResponse,
)
def get_evaluation_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    run = repository.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    return _to_response(run)


@router.get(
    "/{run_id}/comparison",
    response_model=EvaluationComparisonResponse,
)
def get_evaluation_comparison(
    run_id: int,
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    current = repository.get_run(run_id)

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    previous = repository.get_previous_run(run_id)

    if previous is None:
        raise HTTPException(
            status_code=404,
            detail="No previous evaluation run found.",
        )

    comparison = compare_evaluation_runs(
        previous=previous,
        current=current,
    )

    return EvaluationComparisonResponse(
        retrieval_hit_rate_delta=(comparison.retrieval_hit_rate_delta),
        groundedness_delta=(comparison.groundedness_delta),
        semantic_relevance_delta=(comparison.semantic_relevance_delta),
        source_count_delta=(comparison.source_count_delta),
        overall_pass_rate_delta=(comparison.overall_pass_rate_delta),
    )


@router.get(
    "/{run_id}/snapshot",
    response_model=EvaluationSnapshotResponse,
)
def get_evaluation_snapshot(
    run_id: int,
    db: Session = Depends(get_db),
):
    repository = EvaluationRepository(db)

    run = repository.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    previous = repository.get_previous_run(run_id)

    comparison = None

    if previous is not None:
        from app.ai.evaluation.evaluation_comparator import (
            compare_evaluation_runs,
        )

        comparison = compare_evaluation_runs(
            previous=previous,
            current=run,
        )

    report = {
        "total_cases": run.total_cases,
        "retrieval_hit_rate": run.retrieval_hit_rate,
        "average_groundedness": (run.average_groundedness),
        "average_semantic_relevance": (run.average_semantic_relevance),
        "average_source_count": (run.average_source_count),
        "overall_pass_rate": (run.overall_pass_rate),
    }

    quality_gate = {
        "passed": run.quality_gate_passed,
    }

    comparison_data = None

    if comparison is not None:
        comparison_data = {
            "retrieval_hit_rate_delta": (comparison.retrieval_hit_rate_delta),
            "groundedness_delta": (comparison.groundedness_delta),
            "semantic_relevance_delta": (comparison.semantic_relevance_delta),
            "source_count_delta": (comparison.source_count_delta),
            "overall_pass_rate_delta": (comparison.overall_pass_rate_delta),
        }

    return EvaluationSnapshotResponse(
        dataset_name=run.dataset_name,
        report=report,
        quality_gate=quality_gate,
        comparison=comparison_data,
    )


@router.post(
    "/run",
    response_model=EvaluationRunStartResponse,
    status_code=202,
)
def start_evaluation_run(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    metadata = get_evaluation_metadata()

    runner = EvaluationRunner(
        db=db,
        metadata=metadata,
    )

    evaluation_run = runner.create_run()

    background_tasks.add_task(
        _execute_evaluation_in_background,
        evaluation_run.id,
    )

    return EvaluationRunStartResponse(
        evaluation_run_id=evaluation_run.id,
        status=evaluation_run.status,
    )
