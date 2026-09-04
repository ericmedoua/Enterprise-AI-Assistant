from dataclasses import dataclass

from app.models.evaluation_run import EvaluationRun


TREND_EPSILON = 0.001


@dataclass(frozen=True)
class EvaluationMetricTrend:
    metric_name: str
    previous_value: float
    current_value: float
    delta: float
    direction: str


def calculate_trend_direction(
    previous_value: float,
    current_value: float,
    epsilon: float = TREND_EPSILON,
) -> str:
    delta = current_value - previous_value

    if delta > epsilon:
        return "improving"

    if delta < -epsilon:
        return "declining"

    return "stable"


def calculate_metric_trend(
    metric_name: str,
    previous_value: float,
    current_value: float,
) -> EvaluationMetricTrend:
    delta = current_value - previous_value

    return EvaluationMetricTrend(
        metric_name=metric_name,
        previous_value=previous_value,
        current_value=current_value,
        delta=delta,
        direction=calculate_trend_direction(
            previous_value,
            current_value,
        ),
    )


def build_evaluation_trends(
    previous: EvaluationRun,
    current: EvaluationRun,
) -> list[EvaluationMetricTrend]:
    metrics = [
        (
            "retrieval_hit_rate",
            previous.retrieval_hit_rate,
            current.retrieval_hit_rate,
        ),
        (
            "average_groundedness",
            previous.average_groundedness,
            current.average_groundedness,
        ),
        (
            "average_semantic_relevance",
            previous.average_semantic_relevance,
            current.average_semantic_relevance,
        ),
        (
            "average_source_count",
            previous.average_source_count,
            current.average_source_count,
        ),
        (
            "overall_pass_rate",
            previous.overall_pass_rate,
            current.overall_pass_rate,
        ),
    ]

    return [
        calculate_metric_trend(
            metric_name=metric_name,
            previous_value=previous_value,
            current_value=current_value,
        )
        for metric_name, previous_value, current_value in metrics
    ]
