from unittest.mock import Mock

from app.ai.evaluation.evaluation_run_service import (
    get_evaluation_run_by_id,
)


def test_get_evaluation_run_by_id_returns_repository_result():
    repository = Mock()
    run = Mock(id=25)

    repository.get_run.return_value = run

    result = get_evaluation_run_by_id(
        repository,
        run_id=25,
    )

    assert result is run
    repository.get_run.assert_called_once_with(25)


def test_get_evaluation_run_by_id_returns_none_when_missing():
    repository = Mock()

    repository.get_run.return_value = None

    result = get_evaluation_run_by_id(
        repository,
        run_id=999,
    )

    assert result is None
    repository.get_run.assert_called_once_with(999)
