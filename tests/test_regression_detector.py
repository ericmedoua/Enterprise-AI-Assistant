from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)

from app.ai.evaluation.regression_detector import (
    detect_regression,
)


def test_detects_groundedness_regression():
    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=0.0,
        groundedness_delta=-0.20,
        semantic_relevance_delta=0.05,
        source_count_delta=0.0,
        overall_pass_rate_delta=-0.10,
    )

    result = detect_regression(comparison)

    assert result.regression_detected is True
    assert result.groundedness_regression is True
    assert result.semantic_relevance_regression is False


def test_no_regression_when_metrics_improve():
    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=0.10,
        groundedness_delta=0.05,
        semantic_relevance_delta=0.08,
        source_count_delta=0.0,
        overall_pass_rate_delta=0.50,
    )

    result = detect_regression(comparison)

    assert result.regression_detected is False


def test_tolerance_ignores_small_changes():
    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=-0.005,
        groundedness_delta=-0.008,
        semantic_relevance_delta=-0.004,
        source_count_delta=0.0,
        overall_pass_rate_delta=-0.006,
    )

    result = detect_regression(
        comparison,
        tolerance=0.01,
    )

    assert result.regression_detected is False


def test_tolerance_does_not_hide_large_regression():
    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=-0.05,
        groundedness_delta=-0.02,
        semantic_relevance_delta=0.01,
        source_count_delta=0.0,
        overall_pass_rate_delta=-0.10,
    )

    result = detect_regression(
        comparison,
        tolerance=0.01,
    )

    assert result.regression_detected is True
    assert result.retrieval_regression is True
    assert result.groundedness_regression is True
    assert result.overall_pass_rate_regression is True
