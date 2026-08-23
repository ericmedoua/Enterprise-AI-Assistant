from app.ai.evaluation.evaluation_comparator import (
    compare_evaluation_runs,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def build_evaluation_snapshot(
    repository: EvaluationRepository,
    dataset_name: str,
    report: EvaluationReport,
    quality_gate: QualityGateResult,
    current_run_id: int | None = None,
) -> EvaluationSnapshot:
    """
    Build a snapshot for the current evaluation.

    When current_run_id is supplied, compare that run
    with its immediately previous run.
    """

    comparison = None

    if current_run_id is not None:
        previous = repository.get_previous_run(current_run_id)

        current = repository.get_run(current_run_id)

        if current is not None and previous is not None:
            comparison = compare_evaluation_runs(
                previous=previous,
                current=current,
            )

    return EvaluationSnapshot(
        dataset_name=dataset_name,
        report=report,
        quality_gate=quality_gate,
        comparison=comparison,
    )
