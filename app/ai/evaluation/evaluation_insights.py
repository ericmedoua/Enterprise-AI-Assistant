from dataclasses import dataclass

from app.ai.evaluation.evaluation_regression import EvaluationRegression


@dataclass(frozen=True)
class EvaluationInsight:
    metric_name: str
    severity: str
    message: str


def build_evaluation_insights(
    quality_gate_passed: bool,
    trends: list,
    regressions: list[EvaluationRegression] | None = None,
) -> list[EvaluationInsight]:
    insights = []

    if not quality_gate_passed:
        insights.append(
            EvaluationInsight(
                metric_name="quality_gate",
                severity="critical",
                message="The latest evaluation failed the quality gate.",
            )
        )

    for trend in trends:
        if trend.direction == "declining":
            insights.append(
                EvaluationInsight(
                    metric_name=trend.metric_name,
                    severity="warning",
                    message=(
                        f"{trend.metric_name} is declining compared "
                        "with the previous evaluation."
                    ),
                )
            )

    if regressions:
        for regression in regressions:
            insights.append(
                EvaluationInsight(
                    metric_name=regression.metric_name,
                    severity=regression.severity,
                    message=(
                        f"{regression.metric_name} experienced a "
                        f"{regression.severity} regression."
                    ),
                )
            )

    return insights
