import pytest

from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_metadata import (
    EvaluationMetadata,
)
from app.ai.evaluation.evaluation_runner import (
    EvaluationRunner,
    EVALUATION_STATUS_FAILED,
)
from app.core.constants import (
    EVALUATION_STATUS_QUEUED,
    EVALUATION_STATUS_COMPLETED,
    EVALUATION_STATUS_RUNNING,
)
from datetime import datetime


@patch("app.ai.evaluation.evaluation_runner.build_evaluation_snapshot")
@patch("app.ai.evaluation.evaluation_runner.evaluate_quality_gate")
@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
@patch("app.ai.evaluation.evaluation_runner.log_evaluation_completed")
@patch("app.ai.evaluation.evaluation_runner.log_evaluation_started")
@patch("app.ai.evaluation.evaluation_runner.log_evaluation_created")
@patch("app.ai.evaluation.evaluation_runner.evaluation_event_payload")
@patch("app.ai.evaluation.evaluation_runner.build_evaluation_event")
@patch("app.ai.evaluation.evaluation_runner.app_logger")
def test_evaluation_runner(
    mock_logger,
    mock_event,
    mock_payload,
    mock_created,
    mock_started,
    mock_completed,
    mock_report,
    mock_gate,
    mock_snapshot,
):
    db = Mock()

    metadata = EvaluationMetadata(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    report = Mock(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    gate = Mock(
        passed=True,
    )

    snapshot = Mock()

    observability_event = Mock()

    observability_payload = {
        "event": "rag_evaluation_completed",
        "dataset": "rag-evaluation-v1",
    }

    mock_report.return_value = report
    mock_gate.return_value = gate
    mock_snapshot.return_value = snapshot

    mock_event.return_value = observability_event
    mock_payload.return_value = observability_payload

    repository = Mock()

    saved_run = Mock(
        id=42,
        started_at=datetime(
            2026,
            8,
            30,
            13,
            0,
            0,
        ),
        completed_at=datetime(
            2026,
            8,
            30,
            13,
            0,
            10,
        ),
    )

    repository.create_run.return_value = saved_run
    repository.update_results.return_value = saved_run
    repository.update_status.return_value = saved_run

    with patch(
        "app.ai.evaluation.evaluation_runner.EvaluationRepository",
        return_value=repository,
    ):
        runner = EvaluationRunner(
            db=db,
            metadata=metadata,
        )

        result = runner.run()

    assert result.evaluation_run_id == 42
    assert result.snapshot is snapshot

    mock_report.assert_called_once()
    mock_gate.assert_called_once_with(report)

    repository.create_run.assert_called_once()
    repository.update_results.assert_called_once()
    repository.update_status.assert_called_once_with(
        42,
        EVALUATION_STATUS_RUNNING,
    )

    mock_snapshot.assert_called_once()

    mock_created.assert_called_once_with(
        run_id=42,
        dataset_name="rag-evaluation-v1",
    )

    mock_started.assert_called_once_with(
        run_id=42,
    )

    mock_completed.assert_called_once()

    mock_completed.assert_called_once_with(
        run_id=42,
        duration_seconds=10.0,
        retrieval_hit_rate=1.0,
        groundedness=1.0,
        semantic_relevance=0.60,
        overall_pass_rate=1.0,
        quality_gate_passed=True,
    )

    mock_event.assert_called_once_with(snapshot)
    mock_payload.assert_called_once_with(observability_event)
    mock_logger.info.assert_called()


@patch("app.ai.evaluation.evaluation_runner.log_evaluation_failed")
@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
def test_evaluation_runner_execute_run_marks_failed(
    mock_report,
    mock_failed,
):
    db = Mock()

    metadata = EvaluationMetadata(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    running_run = Mock(
        id=42,
    )

    repository = Mock()

    repository.update_status.return_value = running_run

    mock_report.side_effect = RuntimeError("benchmark failed")

    with patch(
        "app.ai.evaluation.evaluation_runner.EvaluationRepository",
        return_value=repository,
    ):
        runner = EvaluationRunner(
            db=db,
            metadata=metadata,
        )

        with pytest.raises(
            RuntimeError,
            match="benchmark failed",
        ):
            runner.execute_run(42)

    repository.update_status.assert_any_call(
        42,
        EVALUATION_STATUS_RUNNING,
    )

    repository.update_status.assert_any_call(
        42,
        EVALUATION_STATUS_FAILED,
    )

    mock_failed.assert_called_once_with(
        run_id=42,
    )

    repository.update_results.assert_not_called()


@patch("app.ai.evaluation.evaluation_runner.build_evaluation_snapshot")
@patch("app.ai.evaluation.evaluation_runner.evaluate_quality_gate")
@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
@patch("app.ai.evaluation.evaluation_runner.app_logger")
@patch("app.ai.evaluation.evaluation_runner.evaluation_event_payload")
@patch("app.ai.evaluation.evaluation_runner.build_evaluation_event")
def test_evaluation_runner_execute_run(
    mock_event,
    mock_payload,
    mock_logger,
    mock_report,
    mock_gate,
    mock_snapshot,
):
    db = Mock()

    metadata = EvaluationMetadata(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    report = Mock(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    gate = Mock(
        passed=True,
    )

    snapshot = Mock()

    current_run = Mock(
        id=42,
        started_at=datetime(
            2026,
            8,
            30,
            13,
            0,
            0,
        ),
        completed_at=None,
    )

    completed_run = Mock(
        id=42,
        started_at=datetime(
            2026,
            8,
            30,
            13,
            0,
            0,
        ),
        completed_at=datetime(
            2026,
            8,
            30,
            13,
            0,
            10,
        ),
    )

    repository = Mock()

    observability_event = Mock()

    observability_payload = {
        "event": "rag_evaluation_completed",
        "dataset": "rag-evaluation-v1",
    }

    repository.update_status.return_value = current_run

    repository.update_results.return_value = completed_run

    mock_event.return_value = observability_event
    mock_payload.return_value = observability_payload

    mock_report.return_value = report
    mock_gate.return_value = gate
    mock_snapshot.return_value = snapshot

    with patch(
        "app.ai.evaluation.evaluation_runner.EvaluationRepository",
        return_value=repository,
    ):
        runner = EvaluationRunner(
            db=db,
            metadata=metadata,
        )

        result = runner.execute_run(42)

    assert result.evaluation_run_id == 42
    assert result.snapshot is snapshot

    mock_event.assert_called_once_with(snapshot)

    mock_payload.assert_called_once_with(observability_event)

    mock_logger.info.assert_called_once_with(
        f"Evaluation observability event: {observability_payload}"
    )

    repository.update_status.assert_called_once_with(
        42,
        EVALUATION_STATUS_RUNNING,
    )

    repository.update_results.assert_called_once()

    call = repository.update_results.call_args.kwargs

    assert call["run_id"] == 42
    assert call["status"] == (EVALUATION_STATUS_COMPLETED)
    assert call["total_cases"] == 2
    assert call["quality_gate_passed"] is True
