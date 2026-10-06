from unittest.mock import Mock

from app.ai.evaluation.evaluation_previous_run_service import (
    get_previous_evaluation_run,
)


def test_get_previous_evaluation_run_returns_repository_result():
    repository = Mock()
    previous_run = Mock(id=24)

    repository.get_previous_run.return_value = previous_run

    result = get_previous_evaluation_run(
        repository,
        run_id=25,
    )

    assert result is previous_run
    repository.get_previous_run.assert_called_once_with(25)


def test_get_previous_evaluation_run_returns_none_when_missing():
    repository = Mock()

    repository.get_previous_run.return_value = None

    result = get_previous_evaluation_run(
        repository,
        run_id=25,
    )

    assert result is None
    repository.get_previous_run.assert_called_once_with(25)
