from unittest.mock import Mock

from app.ai.evaluation.evaluation_run_mutation_service import (
    cancel_queued_evaluation_run,
    fail_stale_evaluation_run,
)


def test_fail_stale_evaluation_run_returns_repository_result():
    repository = Mock()
    updated_run = Mock(id=25)
    repository.fail_stale_run.return_value = updated_run

    result = fail_stale_evaluation_run(
        repository,
        run_id=25,
    )

    assert result is updated_run
    repository.fail_stale_run.assert_called_once_with(run_id=25)


def test_fail_stale_evaluation_run_returns_none_on_conflict():
    repository = Mock()
    repository.fail_stale_run.return_value = None

    result = fail_stale_evaluation_run(
        repository,
        run_id=30,
    )

    assert result is None
    repository.fail_stale_run.assert_called_once_with(run_id=30)


def test_cancel_queued_evaluation_run_returns_repository_result():
    repository = Mock()
    cancelled_run = Mock(id=50)
    repository.cancel_queued_run.return_value = cancelled_run

    result = cancel_queued_evaluation_run(
        repository,
        run_id=50,
    )

    assert result is cancelled_run
    repository.cancel_queued_run.assert_called_once_with(run_id=50)


def test_cancel_queued_evaluation_run_returns_none_on_conflict():
    repository = Mock()
    repository.cancel_queued_run.return_value = None

    result = cancel_queued_evaluation_run(
        repository,
        run_id=51,
    )

    assert result is None
    repository.cancel_queued_run.assert_called_once_with(run_id=51)
