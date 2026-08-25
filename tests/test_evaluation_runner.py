import pytest

from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_metadata import (
    EvaluationMetadata,
)
from app.ai.evaluation.evaluation_runner import (
    EvaluationRunner,
    EVALUATION_STATUS_FAILED,
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
    repository.update_status.assert_not_called()

    mock_snapshot.assert_called_once()


@patch("app.ai.evaluation.evaluation_runner.run_rag_evaluation_report")
def test_evaluation_runner_marks_failed(
    mock_report,
):
    db = Mock()

    metadata = EvaluationMetadata(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    saved_run = Mock(id=42)

    repository = Mock()
    repository.create_run.return_value = saved_run

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
            runner.run()

    repository.update_status.assert_called_once_with(
        42,
        EVALUATION_STATUS_FAILED,
    )

    repository.update_results.assert_not_called()
