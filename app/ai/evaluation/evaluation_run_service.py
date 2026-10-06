from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def get_evaluation_run_by_id(
    repository: EvaluationRepository,
    run_id: int,
):
    return repository.get_run(run_id)
