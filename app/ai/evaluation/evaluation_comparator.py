from dataclasses import dataclass

from app.models.evaluation_run import EvaluationRun


@dataclass(frozen=True)
class EvaluationComparison:
    retrieval_hit_rate_delta: float
    groundedness_delta: float
    semantic_relevance_delta: float
    source_count_delta: float
    overall_pass_rate_delta: float


def compare_evaluation_runs(
    previous: EvaluationRun,
    current: EvaluationRun,
) -> EvaluationComparison:
    """
    Compare a previous evaluation run with a current run.

    Positive values mean the current run improved.
    Negative values mean the current run regressed.
    """

    return EvaluationComparison(
        retrieval_hit_rate_delta=(
            current.retrieval_hit_rate - previous.retrieval_hit_rate
        ),
        groundedness_delta=(
            current.average_groundedness - previous.average_groundedness
        ),
        semantic_relevance_delta=(
            current.average_semantic_relevance - previous.average_semantic_relevance
        ),
        source_count_delta=(
            current.average_source_count - previous.average_source_count
        ),
        overall_pass_rate_delta=(
            current.overall_pass_rate - previous.overall_pass_rate
        ),
    )
