from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)


def format_evaluation_comparison(
    comparison: EvaluationComparison,
) -> str:
    return "\n".join(
        [
            "EVALUATION COMPARISON",
            "=====================",
            (f"Retrieval delta:         {comparison.retrieval_hit_rate_delta:+.2%}"),
            (f"Groundedness delta:      {comparison.groundedness_delta:+.2%}"),
            (f"Semantic relevance:      {comparison.semantic_relevance_delta:+.2%}"),
            (f"Source count delta:      {comparison.source_count_delta:+.2f}"),
            (f"Overall pass-rate delta: {comparison.overall_pass_rate_delta:+.2%}"),
        ]
    )
