from unittest.mock import Mock, patch


@patch("app.ai.evaluation.cli.SessionLocal")
@patch("app.ai.evaluation.cli.get_evaluation_metadata")
@patch("app.ai.evaluation.cli.EvaluationRunner")
@patch("app.ai.evaluation.cli.format_evaluation_snapshot")
def test_cli_main(
    mock_format_snapshot,
    mock_runner,
    mock_metadata,
    mock_session,
):
    from app.ai.evaluation.cli import main

    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    snapshot = Mock()

    runner_result = Mock(
        snapshot=snapshot,
        evaluation_run_id=42,
    )

    mock_metadata.return_value = metadata
    mock_runner.return_value.run.return_value = runner_result
    mock_format_snapshot.return_value = "RAG EVALUATION SNAPSHOT"

    db = Mock()
    mock_session.return_value = db

    main()

    mock_runner.assert_called_once_with(
        db=db,
        metadata=metadata,
    )

    mock_runner.return_value.run.assert_called_once_with()

    mock_format_snapshot.assert_called_once_with(snapshot)

    db.close.assert_called_once()
