from unittest.mock import patch

from app.core.git_metadata import (
    get_git_commit,
)


def test_get_git_commit():
    result = get_git_commit()

    assert result != "unknown"
    assert len(result) == 40


@patch("app.core.git_metadata.subprocess.run")
def test_get_git_commit_returns_unknown_on_failure(
    mock_run,
):
    mock_run.side_effect = OSError("git unavailable")

    result = get_git_commit()

    assert result == "unknown"
