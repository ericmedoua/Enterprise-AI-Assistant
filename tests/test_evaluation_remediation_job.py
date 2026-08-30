from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_remediation_job import (
    run_stale_evaluation_remediation,
)


@patch("app.ai.evaluation.evaluation_remediation_job.remediate_stale_evaluations")
@patch("app.ai.evaluation.evaluation_remediation_job.SessionLocal")
def test_run_stale_evaluation_remediation(
    mock_session_local,
    mock_remediation,
):
    db = Mock()

    mock_session_local.return_value = db
    mock_remediation.return_value = [25, 27]

    result = run_stale_evaluation_remediation()

    assert result == [25, 27]

    mock_remediation.assert_called_once()

    db.close.assert_called_once()


@patch("app.ai.evaluation.evaluation_remediation_job.remediate_stale_evaluations")
@patch("app.ai.evaluation.evaluation_remediation_job.SessionLocal")
def test_run_stale_evaluation_remediation_when_none_found(
    mock_session_local,
    mock_remediation,
):
    db = Mock()

    mock_session_local.return_value = db
    mock_remediation.return_value = []

    result = run_stale_evaluation_remediation()

    assert result == []

    mock_remediation.assert_called_once()

    db.close.assert_called_once()


@patch("app.ai.evaluation.evaluation_remediation_job.remediate_stale_evaluations")
@patch("app.ai.evaluation.evaluation_remediation_job.SessionLocal")
def test_run_stale_evaluation_remediation_closes_session_on_failure(
    mock_session_local,
    mock_remediation,
):
    db = Mock()

    mock_session_local.return_value = db

    mock_remediation.side_effect = RuntimeError("remediation failed")

    try:
        run_stale_evaluation_remediation()
    except RuntimeError:
        pass

    db.close.assert_called_once()
