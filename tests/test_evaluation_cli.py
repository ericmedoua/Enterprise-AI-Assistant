from unittest.mock import Mock, patch


@patch(
    "app.ai.evaluation.cli.run_evaluation_deployment_gate",
    return_value=0,
)
@patch("app.ai.evaluation.cli.EvaluationRepository")
@patch("app.ai.evaluation.cli.SessionLocal")
@patch("app.ai.evaluation.cli.get_evaluation_metadata")
@patch("app.ai.evaluation.cli.EvaluationRunner")
@patch("app.ai.evaluation.cli.format_evaluation_snapshot")
def test_cli_main(
    mock_format_snapshot,
    mock_runner,
    mock_metadata,
    mock_session,
    mock_repository,
    mock_run_gate,
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

    repository = Mock()
    mock_repository.return_value = repository

    result = main()

    assert result == 0

    mock_runner.assert_called_once_with(
        db=db,
        metadata=metadata,
    )

    mock_runner.return_value.run.assert_called_once_with()

    mock_format_snapshot.assert_called_once_with(snapshot)

    mock_repository.assert_called_once_with(db)

    mock_run_gate.assert_called_once_with(repository)

    db.close.assert_called_once()


@patch(
    "app.ai.evaluation.cli.run_evaluation_deployment_gate",
    return_value=1,
)
@patch("app.ai.evaluation.cli.EvaluationRepository")
@patch("app.ai.evaluation.cli.SessionLocal")
@patch("app.ai.evaluation.cli.get_evaluation_metadata")
@patch("app.ai.evaluation.cli.EvaluationRunner")
@patch("app.ai.evaluation.cli.format_evaluation_snapshot")
def test_cli_main_returns_blocked_exit_code(
    mock_format_snapshot,
    mock_runner,
    mock_metadata,
    mock_session,
    mock_repository,
    mock_run_gate,
):
    from app.ai.evaluation.cli import main

    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    snapshot = Mock()

    mock_metadata.return_value = metadata
    mock_runner.return_value.run.return_value = Mock(
        snapshot=snapshot,
        evaluation_run_id=43,
    )

    mock_format_snapshot.return_value = "RAG EVALUATION SNAPSHOT"

    db = Mock()
    mock_session.return_value = db

    repository = Mock()
    mock_repository.return_value = repository

    result = main()

    assert result == 1

    mock_repository.assert_called_once_with(db)
    mock_run_gate.assert_called_once_with(repository)

    db.close.assert_called_once()
