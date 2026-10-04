from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def get_running_evaluation_runs(
    repository: EvaluationRepository,
):
    return repository.list_running_runs()
