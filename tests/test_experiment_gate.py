import pytest

from app.ai.evaluation.experiment_comparator import (
    ExperimentComparison,
)

from app.ai.evaluation.experiment_gate import (
    ExperimentThresholds,
    evaluate_experiment_gate,
)


def test_experiment_gate_passes_when_candidate_improves():
    comparison = ExperimentComparison(
        retrieval_hit_rate_delta=0.05,
        groundedness_delta=0.10,
        semantic_relevance_delta=0.08,
        overall_pass_rate_delta=0.50,
    )

    result = evaluate_experiment_gate(comparison)

    assert result.passed is True


def test_experiment_gate_fails_on_regression():
    comparison = ExperimentComparison(
        retrieval_hit_rate_delta=0.0,
        groundedness_delta=-0.05,
        semantic_relevance_delta=0.10,
        overall_pass_rate_delta=-0.50,
    )

    result = evaluate_experiment_gate(comparison)

    assert result.passed is False
    assert result.groundedness_passed is False
    assert result.overall_pass_rate_passed is False


def test_experiment_gate_supports_custom_thresholds():
    comparison = ExperimentComparison(
        retrieval_hit_rate_delta=0.01,
        groundedness_delta=0.02,
        semantic_relevance_delta=0.03,
        overall_pass_rate_delta=0.04,
    )

    thresholds = ExperimentThresholds(
        minimum_retrieval_delta=0.01,
        minimum_groundedness_delta=0.02,
        minimum_semantic_relevance_delta=0.03,
        minimum_overall_pass_rate_delta=0.04,
    )

    result = evaluate_experiment_gate(
        comparison,
        thresholds,
    )

    assert result.passed is True
