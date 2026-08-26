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


@patch("app.ai.evaluation.evaluation_runner.build_evaluation_snapshot")
@patch("app.ai.evaluation.evaluation_runner.evaluate_quality_gate")
@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
def test_evaluation_runner(
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

    report = Mock()
    gate = Mock()
    snapshot = Mock()

    mock_report.return_value = report
    mock_gate.return_value = gate
    mock_snapshot.return_value = snapshot

    repository = Mock()

    saved_run = Mock(id=42)

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


@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
def test_evaluation_runner_execute_run_marks_failed(
    mock_report,
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

    assert repository.update_status.call_count == 2

    first_call = repository.update_status.call_args_list[0]

    second_call = repository.update_status.call_args_list[1]

    assert first_call.args == (
        42,
        EVALUATION_STATUS_RUNNING,
    )

    assert second_call.args == (
        42,
        EVALUATION_STATUS_FAILED,
    )

    repository.update_results.assert_not_called()


@patch("app.ai.evaluation.evaluation_runner.build_evaluation_snapshot")
@patch("app.ai.evaluation.evaluation_runner.evaluate_quality_gate")
@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
def test_evaluation_runner_execute_run(
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
    )

    completed_run = Mock(
        id=42,
    )

    repository = Mock()

    repository.update_status.return_value = current_run

    repository.update_results.return_value = completed_run

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
