from datetime import datetime


def calculate_duration_seconds(
    started_at: datetime | None,
    completed_at: datetime | None,
) -> float | None:
    if started_at is None or completed_at is None:
        return None

    return (completed_at - started_at).total_seconds()
