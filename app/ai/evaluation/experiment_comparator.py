from dataclasses import dataclass

from app.models.evaluation_run import EvaluationRun


@dataclass(frozen=True)
class ExperimentComparison:
    retrieval_hit_rate_delta: float
    groundedness_delta: float
    semantic_relevance_delta: float
    overall_pass_rate_delta: float


def compare_experiments(
    baseline: EvaluationRun,
    candidate: EvaluationRun,
) -> ExperimentComparison:
    return ExperimentComparison(
        retrieval_hit_rate_delta=(
            candidate.retrieval_hit_rate - baseline.retrieval_hit_rate
        ),
        groundedness_delta=(
            candidate.average_groundedness - baseline.average_groundedness
        ),
        semantic_relevance_delta=(
            candidate.average_semantic_relevance - baseline.average_semantic_relevance
        ),
        overall_pass_rate_delta=(
            candidate.overall_pass_rate - baseline.overall_pass_rate
        ),
    )
