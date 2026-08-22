from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
    compare_evaluation_runs,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def compare_latest_runs(
    repository: EvaluationRepository,
) -> EvaluationComparison | None:
    """
    Compare the two most recent evaluation runs.

    Returns None when fewer than two runs exist.
    """

    current = repository.get_latest_run()

    if current is None:
        return None

    previous = repository.get_previous_run(current.id)

    if previous is None:
        return None

    return compare_evaluation_runs(
        previous=previous,
        current=current,
    )
