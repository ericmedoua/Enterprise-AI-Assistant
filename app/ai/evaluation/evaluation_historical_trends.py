from dataclasses import dataclass
from datetime import datetime
from app.ai.evaluation.evaluation_trends import (
    calculate_trend_direction,
)
from app.models.evaluation_run import EvaluationRun


@dataclass(frozen=True)
class EvaluationMetricPoint:
    run_id: int
    created_at: datetime
    value: float


@dataclass(frozen=True)
class EvaluationHistoricalTrend:
    metric_name: str
    points: list[EvaluationMetricPoint]
    direction: str


def build_historical_metric_trend(
    metric_name: str,
    runs: list[EvaluationRun],
) -> EvaluationHistoricalTrend:
    if not runs:
        return EvaluationHistoricalTrend(
            metric_name=metric_name,
            points=[],
            direction="stable",
        )

    def get_value(run: EvaluationRun) -> float:
        return float(getattr(run, metric_name))

    points = [
        EvaluationMetricPoint(
            run_id=run.id,
            created_at=run.created_at,
            value=get_value(run),
        )
        for run in reversed(runs)
    ]

    if len(points) < 2:
        direction = "stable"
    else:
        direction = calculate_trend_direction(
            points[0].value,
            points[-1].value,
        )

    return EvaluationHistoricalTrend(
        metric_name=metric_name,
        points=points,
        direction=direction,
    )


EVALUATION_TREND_METRICS = [
    "retrieval_hit_rate",
    "average_groundedness",
    "average_semantic_relevance",
    "average_source_count",
    "overall_pass_rate",
]


def build_historical_evaluation_trends(
    runs: list[EvaluationRun],
) -> list[EvaluationHistoricalTrend]:
    return [
        build_historical_metric_trend(
            metric_name=metric_name,
            runs=runs,
        )
        for metric_name in EVALUATION_TREND_METRICS
    ]
