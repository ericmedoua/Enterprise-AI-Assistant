from unittest.mock import Mock

from app.ai.evaluation.evaluation_stale_service import (
    get_running_evaluation_runs,
)


def test_get_running_evaluation_runs_returns_repository_result():
    repository = Mock()
    running_runs = [Mock(id=25)]

    repository.list_running_runs.return_value = running_runs

    result = get_running_evaluation_runs(repository)

    assert result is running_runs
    repository.list_running_runs.assert_called_once()
