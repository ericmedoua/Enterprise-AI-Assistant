from dataclasses import dataclass

from app.ai.evaluation.stale_evaluation import (
    is_evaluation_stale,
)


@dataclass(frozen=True)
class EvaluationHealth:
    healthy: bool
    running_count: int
    stale_count: int
    cancelled_count: int


def evaluate_health(
    runs,
    cancelled_count: int = 0,
    timeout_seconds: int = 300,
) -> EvaluationHealth:
    stale_count = sum(
        1
        for run in runs
        if is_evaluation_stale(
            status=run.status,
            started_at=run.started_at,
            timeout_seconds=timeout_seconds,
        )
    )

    return EvaluationHealth(
        healthy=stale_count == 0,
        running_count=len(runs),
        stale_count=stale_count,
        cancelled_count=cancelled_count,
    )
