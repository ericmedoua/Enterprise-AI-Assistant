from dataclasses import dataclass

from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)

from app.ai.evaluation.evaluation_history import (
    compare_latest_runs,
)

from app.ai.evaluation.regression_detector import (
    RegressionResult,
    detect_regression,
)

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


@dataclass(frozen=True)
class HistoricalRegressionResult:
    comparison: EvaluationComparison | None
    regression: RegressionResult | None


def analyze_latest_regression(
    repository: EvaluationRepository,
    tolerance: float = 0.0,
) -> HistoricalRegressionResult:

    comparison = compare_latest_runs(repository)

    if comparison is None:
        return HistoricalRegressionResult(
            comparison=None,
            regression=None,
        )

    regression = detect_regression(
        comparison,
        tolerance=tolerance,
    )

    return HistoricalRegressionResult(
        comparison=comparison,
        regression=regression,
    )
