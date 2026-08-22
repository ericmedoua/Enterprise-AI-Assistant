from dataclasses import dataclass

from app.ai.evaluation.experiment_comparator import (
    ExperimentComparison,
)


@dataclass(frozen=True)
class ExperimentThresholds:
    minimum_retrieval_delta: float = 0.0
    minimum_groundedness_delta: float = 0.0
    minimum_semantic_relevance_delta: float = 0.0
    minimum_overall_pass_rate_delta: float = 0.0


@dataclass(frozen=True)
class ExperimentGateResult:
    passed: bool
    retrieval_passed: bool
    groundedness_passed: bool
    semantic_relevance_passed: bool
    overall_pass_rate_passed: bool


def evaluate_experiment_gate(
    comparison: ExperimentComparison,
    thresholds: ExperimentThresholds | None = None,
) -> ExperimentGateResult:
    if thresholds is None:
        thresholds = ExperimentThresholds()

    retrieval_passed = (
        comparison.retrieval_hit_rate_delta >= thresholds.minimum_retrieval_delta
    )

    groundedness_passed = (
        comparison.groundedness_delta >= thresholds.minimum_groundedness_delta
    )

    semantic_relevance_passed = (
        comparison.semantic_relevance_delta
        >= thresholds.minimum_semantic_relevance_delta
    )

    overall_pass_rate_passed = (
        comparison.overall_pass_rate_delta >= thresholds.minimum_overall_pass_rate_delta
    )

    passed = (
        retrieval_passed
        and groundedness_passed
        and semantic_relevance_passed
        and overall_pass_rate_passed
    )

    return ExperimentGateResult(
        passed=passed,
        retrieval_passed=retrieval_passed,
        groundedness_passed=groundedness_passed,
        semantic_relevance_passed=semantic_relevance_passed,
        overall_pass_rate_passed=overall_pass_rate_passed,
    )
