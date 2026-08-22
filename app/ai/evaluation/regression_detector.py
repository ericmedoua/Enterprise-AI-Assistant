from dataclasses import dataclass

from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)


@dataclass(frozen=True)
class RegressionResult:
    regression_detected: bool
    retrieval_regression: bool
    groundedness_regression: bool
    semantic_relevance_regression: bool
    overall_pass_rate_regression: bool


def detect_regression(
    comparison: EvaluationComparison,
    tolerance: float = 0.0,
) -> RegressionResult:
    """
    Detect whether evaluation metrics regressed.

    A metric is considered a regression when its delta
    is below the negative tolerance.
    """

    retrieval_regression = comparison.retrieval_hit_rate_delta < -tolerance

    groundedness_regression = comparison.groundedness_delta < -tolerance

    semantic_relevance_regression = comparison.semantic_relevance_delta < -tolerance

    overall_pass_rate_regression = comparison.overall_pass_rate_delta < -tolerance

    regression_detected = (
        retrieval_regression
        or groundedness_regression
        or semantic_relevance_regression
        or overall_pass_rate_regression
    )

    return RegressionResult(
        regression_detected=regression_detected,
        retrieval_regression=retrieval_regression,
        groundedness_regression=groundedness_regression,
        semantic_relevance_regression=semantic_relevance_regression,
        overall_pass_rate_regression=overall_pass_rate_regression,
    )
