from unittest.mock import Mock, patch

from app.repositories.dependencies import (
    get_evaluation_repository,
)


@patch("app.repositories.dependencies.EvaluationRepository")
def test_get_evaluation_repository_uses_supplied_session(
    mock_repository_class,
):
    db = Mock()
    expected_repository = Mock()

    mock_repository_class.return_value = expected_repository

    result = get_evaluation_repository(db=db)

    assert result is expected_repository
    mock_repository_class.assert_called_once_with(db)
