from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)

from app.ai.evaluation.evaluation_comparison_report import (
    format_evaluation_comparison,
)


def test_format_evaluation_comparison():
    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=-0.10,
        groundedness_delta=-0.20,
        semantic_relevance_delta=0.05,
        source_count_delta=0.50,
        overall_pass_rate_delta=-0.50,
    )

    output = format_evaluation_comparison(comparison)

    assert "Retrieval delta:         -10.00%" in output
    assert "Groundedness delta:      -20.00%" in output
    assert "Semantic relevance:      +5.00%" in output
    assert "Source count delta:      +0.50" in output
    assert "Overall pass-rate delta: -50.00%" in output
