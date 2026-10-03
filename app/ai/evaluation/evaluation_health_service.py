from app.ai.evaluation.evaluation_health import (
    evaluate_health,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def build_evaluation_health(
    repository: EvaluationRepository,
):
    running_runs = repository.list_running_runs()

    cancelled_count = repository.count_cancelled_runs()

    return evaluate_health(
        running_runs,
        cancelled_count=cancelled_count,
    )
