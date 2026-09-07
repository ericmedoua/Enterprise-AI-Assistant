from unittest.mock import Mock

from app.ai.evaluation.evaluation_insights import (
    EvaluationInsight,
)
from app.ai.evaluation.evaluation_insights import build_evaluation_insights
from app.ai.evaluation.evaluation_trends import EvaluationMetricTrend
from app.ai.evaluation.evaluation_regression import EvaluationRegression


def make_trend(
    metric_name: str,
    direction: str,
):
    trend = Mock()
    trend.metric_name = metric_name
    trend.direction = direction

    return trend


def test_quality_gate_failure_creates_critical_insight():
    result = build_evaluation_insights(
        quality_gate_passed=False,
        trends=[],
    )

    assert len(result) == 1

    insight = result[0]

    assert isinstance(
        insight,
        EvaluationInsight,
    )

    assert insight.metric_name == "quality_gate"
    assert insight.severity == "critical"
    assert insight.message == "The latest evaluation failed the quality gate."


def test_declining_metric_creates_warning():
    trends = [
        make_trend(
            "average_groundedness",
            "declining",
        )
    ]

    result = build_evaluation_insights(
        quality_gate_passed=True,
        trends=trends,
    )

    assert len(result) == 1

    insight = result[0]

    assert insight.metric_name == ("average_groundedness")
    assert insight.severity == "warning"
    assert insight.message == (
        "average_groundedness is declining compared with the previous evaluation."
    )


def test_improving_metric_creates_no_insight():
    trends = [
        make_trend(
            "average_groundedness",
            "improving",
        )
    ]

    result = build_evaluation_insights(
        quality_gate_passed=True,
        trends=trends,
    )

    assert result == []


def test_stable_metric_creates_no_insight():
    trends = [
        make_trend(
            "retrieval_hit_rate",
            "stable",
        )
    ]

    result = build_evaluation_insights(
        quality_gate_passed=True,
        trends=trends,
    )

    assert result == []


def test_quality_gate_failure_and_declining_metric():
    trends = [
        make_trend(
            "average_groundedness",
            "declining",
        ),
        make_trend(
            "average_semantic_relevance",
            "declining",
        ),
    ]

    result = build_evaluation_insights(
        quality_gate_passed=False,
        trends=trends,
    )

    assert len(result) == 3

    assert result[0].metric_name == "quality_gate"
    assert result[0].severity == "critical"

    assert result[1].metric_name == ("average_groundedness")
    assert result[1].severity == "warning"

    assert result[2].metric_name == ("average_semantic_relevance")
    assert result[2].severity == "warning"


def test_no_problems_creates_no_insights():
    trends = [
        make_trend(
            "retrieval_hit_rate",
            "stable",
        ),
        make_trend(
            "average_groundedness",
            "improving",
        ),
    ]

    result = build_evaluation_insights(
        quality_gate_passed=True,
        trends=trends,
    )

    assert result == []


def test_build_evaluation_insights_with_quality_gate_failure_and_declining_metric():
    declining_trend = EvaluationMetricTrend(
        metric_name="average_groundedness",
        previous_value=0.90,
        current_value=0.75,
        delta=-0.15,
        direction="declining",
    )

    insights = build_evaluation_insights(
        quality_gate_passed=False,
        trends=[declining_trend],
    )

    assert len(insights) == 2

    assert insights[0].metric_name == "quality_gate"
    assert insights[0].severity == "critical"

    assert insights[1].metric_name == "average_groundedness"
    assert insights[1].severity == "warning"


def test_build_evaluation_insights_without_regressions():
    insights = build_evaluation_insights(
        quality_gate_passed=True,
        trends=[],
    )

    assert insights == []


def test_build_evaluation_insights_with_regression():
    regression = EvaluationRegression(
        metric_name="average_groundedness",
        previous_value=0.90,
        current_value=0.70,
        delta=-0.20,
        severity="critical",
    )

    insights = build_evaluation_insights(
        quality_gate_passed=True,
        trends=[],
        regressions=[regression],
    )

    assert len(insights) == 1
    assert insights[0].metric_name == "average_groundedness"
    assert insights[0].severity == "critical"
    assert "regression" in insights[0].message.lower()
