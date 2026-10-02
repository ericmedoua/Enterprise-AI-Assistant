from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def get_latest_evaluation_run(
    repository: EvaluationRepository,
):
    return repository.get_latest_run()
