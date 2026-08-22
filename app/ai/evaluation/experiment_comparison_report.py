from app.ai.evaluation.experiment_comparator import (
    ExperimentComparison,
)


def format_experiment_comparison(
    comparison: ExperimentComparison,
) -> str:
    return "\n".join(
        [
            "EXPERIMENT COMPARISON",
            "=====================",
            (f"Retrieval delta:         {comparison.retrieval_hit_rate_delta:+.2%}"),
            (f"Groundedness delta:      {comparison.groundedness_delta:+.2%}"),
            (f"Semantic relevance:      {comparison.semantic_relevance_delta:+.2%}"),
            (f"Overall pass-rate delta: {comparison.overall_pass_rate_delta:+.2%}"),
        ]
    )
