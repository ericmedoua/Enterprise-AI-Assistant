from dataclasses import dataclass

from app.ai.evaluation.evaluation_trends import EvaluationMetricTrend

import math


REGRESSION_EPSILON = 0.05


@dataclass(frozen=True)
class EvaluationRegression:
    metric_name: str
    previous_value: float
    current_value: float
    delta: float
    severity: str


def is_metric_regression(
    trend: EvaluationMetricTrend,
    epsilon: float = REGRESSION_EPSILON,
) -> bool:
    if math.isclose(trend.delta, -epsilon, abs_tol=1e-9):
        return False

    return trend.delta < -epsilon


def classify_regression_severity(
    delta: float,
) -> str:
    if delta <= -0.20:
        return "critical"

    if delta <= -0.05:
        return "warning"

    return "none"


def detect_metric_regression(
    trend: EvaluationMetricTrend,
    epsilon: float = REGRESSION_EPSILON,
) -> EvaluationRegression | None:
    if not is_metric_regression(trend, epsilon=epsilon):
        return None

    return EvaluationRegression(
        metric_name=trend.metric_name,
        previous_value=trend.previous_value,
        current_value=trend.current_value,
        delta=trend.delta,
        severity=classify_regression_severity(trend.delta),
    )


def detect_evaluation_regressions(
    trends: list[EvaluationMetricTrend],
    epsilon: float = REGRESSION_EPSILON,
) -> list[EvaluationRegression]:
    regressions = []

    for trend in trends:
        regression = detect_metric_regression(
            trend,
            epsilon=epsilon,
        )

        if regression is not None:
            regressions.append(regression)

    return regressions
