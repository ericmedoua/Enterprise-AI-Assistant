from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def fail_stale_evaluation_run(
    repository: EvaluationRepository,
    run_id: int,
):
    return repository.fail_stale_run(
        run_id=run_id,
    )


def cancel_queued_evaluation_run(
    repository: EvaluationRepository,
    run_id: int,
):
    return repository.cancel_queued_run(
        run_id=run_id,
    )
