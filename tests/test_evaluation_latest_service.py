from unittest.mock import Mock

from app.ai.evaluation.evaluation_latest_service import (
    get_latest_evaluation_run,
)


def test_get_latest_evaluation_run_returns_repository_result():
    repository = Mock()
    latest_run = Mock(id=42)

    repository.get_latest_run.return_value = latest_run

    result = get_latest_evaluation_run(repository)

    assert result is latest_run
    repository.get_latest_run.assert_called_once()
