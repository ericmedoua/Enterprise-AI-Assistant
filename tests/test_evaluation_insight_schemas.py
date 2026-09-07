from app.schemas.evaluation import (
    EvaluationInsightResponse,
)


def test_evaluation_insight_response():
    result = EvaluationInsightResponse(
        metric_name="average_groundedness",
        severity="warning",
        message=(
            "average_groundedness is declining compared with the previous evaluation."
        ),
    )

    assert result.metric_name == ("average_groundedness")
    assert result.severity == "warning"
    assert result.message == (
        "average_groundedness is declining compared with the previous evaluation."
    )


def test_evaluation_insight_response_critical():
    result = EvaluationInsightResponse(
        metric_name="quality_gate",
        severity="critical",
        message=("The latest evaluation failed the quality gate."),
    )

    assert result.metric_name == "quality_gate"
    assert result.severity == "critical"
