from app.ai.evaluation.evaluation_history import (
    build_evaluation_history,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def get_evaluation_observability_history(
    repository: EvaluationRepository,
):
    runs = repository.list_runs()

    return build_evaluation_history(runs)
