import subprocess


def get_git_commit() -> str:
    """
    Return the current Git commit hash.

    Returns 'unknown' when the repository metadata
    is unavailable.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        commit = result.stdout.strip()

        return commit or "unknown"

    except (
        OSError,
        subprocess.CalledProcessError,
    ):
        return "unknown"
