from datetime import datetime, timedelta, timezone


def is_evaluation_stale(
    status: str,
    started_at: datetime | None,
    timeout_seconds: int = 300,
) -> bool:
    if status != "running":
        return False

    if started_at is None:
        return False

    now = datetime.now(timezone.utc)

    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)

    age = now - started_at

    return age > timedelta(seconds=timeout_seconds)
