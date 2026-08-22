from unittest.mock import patch

from app.ai.evaluation.evaluation_metadata import (
    get_evaluation_metadata,
)


@patch("app.ai.evaluation.evaluation_metadata.get_git_commit")
def test_get_evaluation_metadata(
    mock_get_git_commit,
):
    mock_get_git_commit.return_value = "a" * 40

    metadata = get_evaluation_metadata()

    assert metadata.llm_model != ""
    assert metadata.embedding_model != ""
    assert metadata.git_commit == "a" * 40
