from unittest.mock import Mock

from app.repositories.evaluation_repository import (
    EvaluationRepository,
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

    result = repository.create_from_evaluation(
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        report=report,
        quality_gate=quality_gate,
    )

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
