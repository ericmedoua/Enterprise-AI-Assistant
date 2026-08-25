from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)


@patch("app.ai.evaluation.cli.SessionLocal")
@patch("app.ai.evaluation.cli.EvaluationRepository")
@patch("app.ai.evaluation.cli.get_evaluation_metadata")
@patch("app.ai.evaluation.cli.evaluate_quality_gate")
@patch("app.ai.evaluation.cli.run_rag_evaluation_report")
@patch("app.ai.evaluation.cli.build_evaluation_snapshot")
@patch("app.ai.evaluation.cli.format_evaluation_snapshot")
def test_cli_main(
    mock_format_snapshot,
    mock_build_snapshot,
    mock_report,
    mock_gate,
    mock_metadata,
    mock_repository,
    mock_session,
):
    from app.ai.evaluation.cli import main

    report = Mock(
        total_cases=2,
    )

    gate = Mock(
        passed=True,
    )

    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    current_run = Mock(
        id=10,
    )

    snapshot = Mock(
        spec=EvaluationSnapshot,
    )

    mock_report.return_value = report
    mock_gate.return_value = gate
    mock_metadata.return_value = metadata

    mock_repository.return_value.create_from_evaluation.return_value = current_run

    mock_build_snapshot.return_value = snapshot
    mock_format_snapshot.return_value = "RAG EVALUATION SNAPSHOT"

    db = Mock()
    mock_session.return_value = db

    main()

    mock_report.assert_called_once()

    mock_gate.assert_called_once_with(report)

    mock_metadata.assert_called_once()

    mock_repository.return_value.create_from_evaluation.assert_called_once_with(
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
        report=report,
        quality_gate=gate,
    )

    mock_build_snapshot_call = mock_build_snapshot.call_args

    assert mock_build_snapshot_call.kwargs["current_run_id"] == 10

    mock_format_snapshot.assert_called_once_with(snapshot)

    db.close.assert_called_once()
