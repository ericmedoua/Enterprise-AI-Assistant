from app.ai.evaluation.stale_evaluation import (
    is_evaluation_stale,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def remediate_stale_evaluations(
    repository: EvaluationRepository,
    timeout_seconds: int = 300,
) -> list[int]:
    """
    Find running evaluations that have exceeded the
    configured timeout and mark them as failed.

    Returns the IDs of evaluations successfully
    remediated.
    """

    running_runs = repository.list_running_runs()

    remediated_ids: list[int] = []

    for run in running_runs:
        if not is_evaluation_stale(
            status=run.status,
            started_at=run.started_at,
            timeout_seconds=timeout_seconds,
        ):
            continue

        updated_run = repository.fail_stale_run(
            run_id=run.id,
            timeout_seconds=timeout_seconds,
        )

        if updated_run is not None:
            remediated_ids.append(run.id)

    return remediated_ids
