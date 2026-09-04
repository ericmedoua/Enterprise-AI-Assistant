import pytest

from unittest.mock import Mock

from app.ai.evaluation.evaluation_history import (
    compare_latest_runs,
)

from datetime import datetime, timedelta

from app.ai.evaluation.evaluation_history import (
    build_evaluation_history,
)
from app.models.evaluation_run import EvaluationRun


def test_compare_latest_runs():
    repository = Mock()

    previous = Mock(
        id=1,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    current = Mock(
        id=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.75,
        average_semantic_relevance=0.65,
        average_source_count=1.0,
        overall_pass_rate=0.50,
    )

    repository.get_latest_run.return_value = current
    repository.get_previous_run.return_value = previous

    result = compare_latest_runs(repository)

    assert result is not None
    assert result.groundedness_delta == pytest.approx(-0.25)
    assert result.semantic_relevance_delta == pytest.approx(0.05)
    assert result.overall_pass_rate_delta == pytest.approx(-0.50)


def test_compare_latest_runs_returns_none_without_current():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = compare_latest_runs(repository)

    assert result is None


def test_compare_latest_runs_returns_none_without_previous():
    repository = Mock()

    current = Mock(id=1)

    repository.get_latest_run.return_value = current
    repository.get_previous_run.return_value = None

    result = compare_latest_runs(repository)

    assert result is None


def make_run(run_id: int) -> EvaluationRun:
    started_at = datetime(
        2026,
        8,
        31,
        20,
        0,
        0,
    )

    completed_at = started_at + timedelta(seconds=10)

    return EvaluationRun(
        id=run_id,
        created_at=started_at,
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
        status="completed",
        started_at=started_at,
        completed_at=completed_at,
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
        quality_gate_passed=True,
    )


def test_build_evaluation_history():
    runs = [
        make_run(1),
        make_run(2),
    ]

    result = build_evaluation_history(runs)

    assert len(result.runs) == 2

    assert result.runs[0].id == 1
    assert result.runs[1].id == 2

    assert result.runs[0].status == "completed"

    assert result.runs[0].duration_seconds == 10.0

    assert result.runs[0].retrieval_hit_rate == 1.0
    assert result.runs[0].average_groundedness == 1.0
    assert result.runs[0].average_semantic_relevance == 0.60
    assert result.runs[0].overall_pass_rate == 1.0

    assert result.runs[0].quality_gate_passed is True


def test_build_evaluation_history_empty():
    result = build_evaluation_history([])

    assert result.runs == []


def test_build_evaluation_history_running_run():
    started_at = datetime(
        2026,
        8,
        31,
        20,
        0,
        0,
    )

    run = EvaluationRun(
        id=3,
        created_at=started_at,
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
        status="running",
        started_at=started_at,
        completed_at=None,
        total_cases=0,
        retrieval_hit_rate=0.0,
        average_groundedness=0.0,
        average_semantic_relevance=0.0,
        average_source_count=0.0,
        overall_pass_rate=0.0,
        quality_gate_passed=False,
    )

    result = build_evaluation_history([run])

    assert len(result.runs) == 1
    assert result.runs[0].status == "running"
    assert result.runs[0].duration_seconds is None
