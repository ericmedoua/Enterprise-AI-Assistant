from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.schemas.evaluation import (
    EvaluationHistoryResponse,
    EvaluationRunResponse,
    EvaluationSnapshotResponse,
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
        total_cases=run.total_cases,
        retrieval_hit_rate=run.retrieval_hit_rate,
        average_groundedness=run.average_groundedness,
        average_semantic_relevance=(run.average_semantic_relevance),
        average_source_count=run.average_source_count,
        overall_pass_rate=run.overall_pass_rate,
        quality_gate_passed=run.quality_gate_passed,
    )


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

    latest = repository.get_latest_run()

    if latest is None:
        raise HTTPException(
            status_code=404,
            detail="No evaluation runs found.",
        )

    previous = repository.get_previous_run(latest.id)

    comparison_response = None

    if previous is not None:
        comparison = compare_evaluation_runs(
            previous=previous,
            current=latest,
        )

        comparison_response = EvaluationComparisonResponse(
            retrieval_hit_rate_delta=(comparison.retrieval_hit_rate_delta),
            groundedness_delta=(comparison.groundedness_delta),
            semantic_relevance_delta=(comparison.semantic_relevance_delta),
            source_count_delta=(comparison.source_count_delta),
            overall_pass_rate_delta=(comparison.overall_pass_rate_delta),
        )

    return EvaluationDashboardResponse(
        latest=_to_response(latest),
        comparison=comparison_response,
    )


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
