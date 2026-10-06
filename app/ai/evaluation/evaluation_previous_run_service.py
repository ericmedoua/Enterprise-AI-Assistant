from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def get_previous_evaluation_run(
    repository: EvaluationRepository,
    run_id: int,
):
    return repository.get_previous_run(run_id)
