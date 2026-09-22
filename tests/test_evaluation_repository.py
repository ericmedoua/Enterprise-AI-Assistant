from unittest.mock import Mock

import pytest

from app.core.constants import EVALUATION_STATUS_COMPLETED
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.models.evaluation_run import (
    EvaluationRun,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)

from datetime import (
    datetime,
    timedelta,
    timezone,
)


def test_create_run():
    db = Mock()

    repository = EvaluationRepository(db)

    result = repository.create_run(
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.5971,
        average_source_count=1.0,
        overall_pass_rate=1.0,
        quality_gate_passed=True,
    )

    assert result.dataset_name == ("rag-evaluation-v1")

    assert result.total_cases == 2
    assert result.retrieval_hit_rate == 1.0
    assert result.quality_gate_passed is True

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_from_evaluation():
    db = Mock()

    repository = EvaluationRepository(db)

    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.5971,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    quality_gate = QualityGateResult(
        passed=True,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=True,
    )

    result = repository.create_run_from_report(
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        report=report,
        quality_gate=quality_gate,
    )

    assert result is not None

    assert result.dataset_name == ("rag-evaluation-v1")

    assert result.llm_model == "openai/gpt-oss-120b"
    assert result.embedding_model == "all-MiniLM-L6-v2"
    assert result.git_commit == "test-commit"

    assert result.total_cases == 2
    assert result.retrieval_hit_rate == 1.0
    assert result.average_groundedness == 1.0
    assert result.average_semantic_relevance == 0.5971
    assert result.average_source_count == 1.0
    assert result.overall_pass_rate == 1.0
    assert result.quality_gate_passed is True


def test_get_latest_run():
    db = Mock()

    repository = EvaluationRepository(db)

    latest = Mock()

    db.query.return_value.order_by.return_value.first.return_value = latest

    result = repository.get_latest_run()

    assert result is latest


def test_get_previous_run():
    db = Mock()

    repository = EvaluationRepository(db)

    previous = Mock()

    (
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value
    ) = previous

    result = repository.get_previous_run(current_run_id=10)

    assert result is previous

    db.query.return_value.filter.assert_called_once()


def test_get_previous_compatible_run():
    db = Mock()

    repository = EvaluationRepository(db)

    current = Mock(
        id=10,
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        total_cases=8,
    )

    previous = Mock()

    (
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value
    ) = previous

    result = repository.get_previous_compatible_run(current)

    assert result is previous

    db.query.return_value.filter.assert_called_once()


def test_list_runs_by_dataset():
    db = Mock()

    repository = EvaluationRepository(db)

    expected = [Mock()]

    (
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value
    ) = expected

    result = repository.list_runs_by_dataset("rag-evaluation-v1")

    assert result is expected


def test_list_runs_by_model():
    db = Mock()

    repository = EvaluationRepository(db)

    expected = [Mock()]

    (
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value
    ) = expected

    result = repository.list_runs_by_model(
        "openai/gpt-oss-120b",
        "all-MiniLM-L6-v2",
    )

    assert result is expected


def test_update_status():
    db = Mock()

    run = Mock(
        id=10,
        status="queued",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.update_status(
        run_id=10,
        status="running",
    )

    assert result is run
    assert run.status == "running"
    assert run.started_at is not None
    assert run.completed_at is None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_update_results():
    db = Mock()

    run = Mock(
        id=10,
        status="running",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.update_results(
        run_id=10,
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.95,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
        quality_gate_passed=True,
        status="completed",
    )

    assert result is run

    assert run.total_cases == 2
    assert run.retrieval_hit_rate == 1.0
    assert run.average_groundedness == 0.95
    assert run.average_semantic_relevance == 0.60
    assert run.average_source_count == 1.0
    assert run.overall_pass_rate == 1.0
    assert run.quality_gate_passed is True

    assert run.status == "completed"
    assert run.completed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_update_results_failed():
    db = Mock()

    run = Mock(
        id=10,
        status="running",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.update_results(
        run_id=10,
        total_cases=0,
        retrieval_hit_rate=0.0,
        average_groundedness=0.0,
        average_semantic_relevance=0.0,
        average_source_count=0.0,
        overall_pass_rate=0.0,
        quality_gate_passed=False,
        status="failed",
    )

    assert result is run
    assert run.status == "failed"
    assert run.completed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_list_running_runs():
    db = Mock()

    expected = [Mock()]

    (
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value
    ) = expected

    repository = EvaluationRepository(db)

    result = repository.list_running_runs()

    assert result is expected


def test_fail_stale_run():
    db = Mock()

    run = Mock(
        id=25,
        status="running",
        started_at=(datetime.now(timezone.utc) - timedelta(hours=1)),
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.fail_stale_run(
        run_id=25,
        timeout_seconds=300,
    )

    assert result is run
    assert run.status == "failed"
    assert run.completed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_fail_stale_run_does_not_fail_recent_run():
    db = Mock()

    run = Mock(
        id=26,
        status="running",
        started_at=datetime.now(timezone.utc),
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.fail_stale_run(
        run_id=26,
        timeout_seconds=300,
    )

    assert result is None
    assert run.status == "running"
    assert run.completed_at is None

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_fail_stale_run_does_not_change_completed_run():
    db = Mock()

    run = Mock(
        id=27,
        status="completed",
        started_at=(datetime.now(timezone.utc) - timedelta(hours=1)),
        completed_at=(datetime.now(timezone.utc)),
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.fail_stale_run(
        run_id=27,
        timeout_seconds=300,
    )

    assert result is None
    assert run.status == "completed"

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_cancel_queued_run():
    db = Mock()

    run = Mock(
        id=50,
        status="queued",
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.cancel_queued_run(
        run_id=50,
    )

    assert result is run
    assert run.status == "cancelled"
    assert run.completed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(run)


def test_cancel_queued_run_does_not_cancel_running_run():
    db = Mock()

    run = Mock(
        id=51,
        status="running",
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.cancel_queued_run(
        run_id=51,
    )

    assert result is None
    assert run.status == "running"
    assert run.completed_at is None

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_cancel_queued_run_does_not_cancel_completed_run():
    db = Mock()

    run = Mock(
        id=52,
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.cancel_queued_run(
        run_id=52,
    )

    assert result is None
    assert run.status == "completed"

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_cancel_queued_run_not_found():
    db = Mock()

    db.get.return_value = None

    repository = EvaluationRepository(db)

    result = repository.cancel_queued_run(
        run_id=999,
    )

    assert result is None

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_list_runs_with_limit():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value
    limited_query = ordered_query.limit.return_value

    runs = [
        Mock(id=3),
        Mock(id=2),
    ]

    limited_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(limit=2)

    assert result == runs

    db.query.assert_called_once_with(EvaluationRun)

    query.order_by.assert_called_once()

    order_by_args = query.order_by.call_args.args

    assert len(order_by_args) == 2
    assert str(order_by_args[0]) == str(EvaluationRun.created_at.desc())
    assert str(order_by_args[1]) == str(EvaluationRun.id.desc())

    ordered_query.limit.assert_called_once_with(2)

    limited_query.all.assert_called_once()


def test_list_runs_with_limit_and_offset():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value
    offset_query = ordered_query.offset.return_value
    limited_query = offset_query.limit.return_value

    runs = [
        Mock(id=1),
        Mock(id=0),
    ]

    limited_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(
        limit=2,
        offset=2,
    )

    assert result == runs

    ordered_query.offset.assert_called_once_with(2)
    offset_query.limit.assert_called_once_with(2)
    limited_query.all.assert_called_once()


def test_list_runs_with_zero_offset_does_not_call_offset():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value

    runs = [Mock(id=3)]

    ordered_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(offset=0)

    assert result == runs
    ordered_query.offset.assert_not_called()


def test_list_runs_without_limit():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value

    runs = [
        Mock(id=3),
        Mock(id=2),
        Mock(id=1),
    ]

    ordered_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs()

    assert result == runs

    db.query.assert_called_once_with(EvaluationRun)

    query.order_by.assert_called_once()

    order_by_args = query.order_by.call_args.args

    assert len(order_by_args) == 2
    assert str(order_by_args[0]) == str(EvaluationRun.created_at.desc())
    assert str(order_by_args[1]) == str(EvaluationRun.id.desc())

    ordered_query.all.assert_called_once()

    ordered_query.limit.assert_not_called()


def test_list_runs_with_zero_limit():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value
    limited_query = ordered_query.limit.return_value

    limited_query.all.return_value = []

    repository = EvaluationRepository(db)

    result = repository.list_runs(limit=0)

    assert result == []

    ordered_query.limit.assert_called_once_with(0)
    limited_query.all.assert_called_once()


def test_update_status_allows_queued_to_running():
    db = Mock()

    run = Mock(
        id=10,
        status="queued",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    result = repository.update_status(
        run_id=10,
        status="running",
    )

    assert result is run
    assert run.status == "running"
    assert run.started_at is not None


def test_update_status_rejects_completed_to_running():
    db = Mock()

    run = Mock(
        id=10,
        status="completed",
        started_at=None,
        completed_at=datetime.now(timezone.utc),
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    with pytest.raises(ValueError, match="Invalid evaluation status transition"):
        repository.update_status(
            run_id=10,
            status="running",
        )

    assert run.status == "completed"
    db.commit.assert_not_called()


def test_update_status_rejects_unknown_status():
    db = Mock()

    run = Mock(
        id=10,
        status="queued",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    with pytest.raises(ValueError, match="Invalid evaluation status transition"):
        repository.update_status(
            run_id=10,
            status="completed",
        )

    assert run.status == "queued"
    db.commit.assert_not_called()


def test_create_run_rejects_metric_above_one():
    db = Mock()

    repository = EvaluationRepository(db)

    with pytest.raises(
        ValueError,
        match="retrieval_hit_rate must be between 0.0 and 1.0",
    ):
        repository.create_run(
            dataset_name="rag-evaluation-v1",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.1,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_update_results_rejects_negative_metric():
    db = Mock()

    run = Mock(
        id=10,
        status="running",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    with pytest.raises(
        ValueError,
        match="average_groundedness must be between 0.0 and 1.0",
    ):
        repository.update_results(
            run_id=10,
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=-0.1,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
            status="completed",
        )

    db.commit.assert_not_called()


def test_create_run_rejects_negative_source_count():
    db = Mock()

    repository = EvaluationRepository(db)

    with pytest.raises(
        ValueError,
        match="average_source_count must be greater than or equal to 0",
    ):
        repository.create_run(
            dataset_name="rag-evaluation-v1",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=-1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_update_results_rejects_zero_cases_for_completed_run():
    db = Mock()

    run = Mock(
        id=10,
        status="running",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    with pytest.raises(
        ValueError,
        match="total_cases must be greater than 0",
    ):
        repository.update_results(
            run_id=10,
            total_cases=0,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
            status="completed",
        )

    db.commit.assert_not_called()


def test_update_results_rejects_non_running_run():
    db = Mock()

    run = Mock(
        id=10,
        status="queued",
        started_at=None,
        completed_at=None,
    )

    db.get.return_value = run

    repository = EvaluationRepository(db)

    with pytest.raises(
        ValueError,
        match="Evaluation results can only be updated for running runs",
    ):
        repository.update_results(
            run_id=10,
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
            status=EVALUATION_STATUS_COMPLETED,
        )

    assert run.status == "queued"
    db.commit.assert_not_called()


def test_count_runs():
    db = Mock()

    query = db.query.return_value
    query.count.return_value = 5

    repository = EvaluationRepository(db)

    result = repository.count_runs()

    assert result == 5

    db.query.assert_called_once_with(EvaluationRun)
    query.count.assert_called_once()


def test_list_runs_with_dataset_filter():
    db = Mock()

    query = db.query.return_value
    filtered_query = query.filter.return_value
    ordered_query = filtered_query.order_by.return_value

    runs = [Mock(id=5)]
    ordered_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(
        dataset_name="rag-evaluation-v1",
    )

    assert result == runs

    query.filter.assert_called_once()
    ordered_query.all.assert_called_once()


def test_list_runs_with_multiple_filters():
    db = Mock()

    query = db.query.return_value
    filtered_once = query.filter.return_value
    filtered_twice = filtered_once.filter.return_value
    filtered_thrice = filtered_twice.filter.return_value
    ordered_query = filtered_thrice.order_by.return_value

    runs = [Mock(id=7)]
    ordered_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(
        dataset_name="rag-evaluation-v1",
        status="completed",
        quality_gate_passed=True,
    )

    assert result == runs

    query.filter.assert_called_once()
    filtered_once.filter.assert_called_once()
    filtered_twice.filter.assert_called_once()
    ordered_query.all.assert_called_once()


def test_count_runs_with_filters():
    db = Mock()

    query = db.query.return_value
    filtered_query = query.filter.return_value

    filtered_query.filter.return_value = filtered_query
    filtered_query.count.return_value = 12

    repository = EvaluationRepository(db)

    result = repository.count_runs(
        dataset_name="rag-evaluation-v1",
        status="completed",
        quality_gate_passed=True,
    )

    assert result == 12

    query.filter.assert_called_once()
    filtered_query.filter.assert_called()
    filtered_query.count.assert_called_once()


def test_list_runs_sorts_by_groundedness_ascending():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value

    runs = [Mock(id=2), Mock(id=1)]
    ordered_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(
        sort_by="average_groundedness",
        sort_order="asc",
    )

    assert result == runs

    query.order_by.assert_called_once()

    order_by_args = query.order_by.call_args.args

    assert len(order_by_args) == 3
    assert str(order_by_args[0]) == str(EvaluationRun.average_groundedness.asc())
    assert str(order_by_args[1]) == str(EvaluationRun.created_at.desc())
    assert str(order_by_args[2]) == str(EvaluationRun.id.desc())

    ordered_query.all.assert_called_once()


def test_list_runs_sorts_by_overall_pass_rate_descending():
    db = Mock()

    query = db.query.return_value
    ordered_query = query.order_by.return_value

    runs = [Mock(id=5)]
    ordered_query.all.return_value = runs

    repository = EvaluationRepository(db)

    result = repository.list_runs(
        sort_by="overall_pass_rate",
        sort_order="desc",
    )

    assert result == runs

    query.order_by.assert_called_once()

    order_by_args = query.order_by.call_args.args

    assert len(order_by_args) == 3
    assert str(order_by_args[0]) == str(EvaluationRun.overall_pass_rate.desc())
    assert str(order_by_args[1]) == str(EvaluationRun.created_at.desc())
    assert str(order_by_args[2]) == str(EvaluationRun.id.desc())


def test_list_runs_rejects_unsupported_sort_order():
    db = Mock()

    repository = EvaluationRepository(db)

    with pytest.raises(
        ValueError,
        match="Unsupported evaluation history sort order",
    ):
        repository.list_runs(
            sort_order="sideways",
        )
