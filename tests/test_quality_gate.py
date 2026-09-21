from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityThresholds,
    evaluate_quality_gate,
)


def make_report(
    retrieval=1.0,
    groundedness=1.0,
    relevance=0.60,
    overall=1.0,
):
    return EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=retrieval,
        average_groundedness=groundedness,
        average_semantic_relevance=relevance,
        average_source_count=1.0,
        overall_pass_rate=overall,
    )


def test_quality_gate_passes_good_report():
    report = make_report()

    result = evaluate_quality_gate(report)

    assert result.passed is True
    assert result.retrieval_passed is True
    assert result.groundedness_passed is True
    assert result.semantic_relevance_passed is True
    assert result.overall_passed is True


def test_quality_gate_fails_retrieval_regression():
    report = make_report(
        retrieval=0.5,
    )

    result = evaluate_quality_gate(report)

    assert result.passed is False
    assert result.retrieval_passed is False


def test_quality_gate_fails_groundedness_regression():
    report = make_report(
        groundedness=0.80,
    )

    result = evaluate_quality_gate(report)

    assert result.passed is False
    assert result.groundedness_passed is False


def test_quality_gate_fails_relevance_regression():
    report = make_report(
        relevance=0.40,
    )

    result = evaluate_quality_gate(report)

    assert result.passed is False
    assert result.semantic_relevance_passed is False


def test_quality_gate_fails_overall_pass_rate_regression():
    report = make_report(
        overall=0.50,
    )

    result = evaluate_quality_gate(report)

    assert result.passed is False
    assert result.overall_passed is False


def test_custom_quality_thresholds():
    report = make_report(
        retrieval=0.90,
        groundedness=0.85,
        relevance=0.45,
        overall=0.90,
    )

    thresholds = QualityThresholds(
        minimum_retrieval_hit_rate=0.90,
        minimum_groundedness=0.85,
        minimum_semantic_relevance=0.45,
        minimum_overall_pass_rate=0.90,
    )

    result = evaluate_quality_gate(
        report,
        thresholds,
    )

    assert result.passed is True


def test_quality_gate_reports_failed_metrics():
    report = make_report(
        retrieval=0.80,
        groundedness=0.75,
        relevance=0.40,
        overall=0.50,
    )

    result = evaluate_quality_gate(report)

    assert result.passed is False
    assert len(result.failures) == 4

    assert result.failures[0].metric_name == "retrieval_hit_rate"
    assert result.failures[0].actual_value == 0.80
    assert result.failures[0].required_value == 1.0

    assert result.failures[1].metric_name == "average_groundedness"
    assert result.failures[1].actual_value == 0.75
    assert result.failures[1].required_value == 0.90

    assert result.failures[2].metric_name == "average_semantic_relevance"
    assert result.failures[2].actual_value == 0.40
    assert result.failures[2].required_value == 0.50

    assert result.failures[3].metric_name == "overall_pass_rate"
    assert result.failures[3].actual_value == 0.50
    assert result.failures[3].required_value == 1.0


def test_quality_gate_has_no_failures_when_passing():
    result = evaluate_quality_gate(make_report())

    assert result.passed is True
    assert result.failures == ()
