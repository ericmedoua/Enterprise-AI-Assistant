from app.ai.evaluation.experiment_comparator import (
    ExperimentComparison,
)

from app.ai.evaluation.experiment_comparison_report import (
    format_experiment_comparison,
)


def test_format_experiment_comparison():
    comparison = ExperimentComparison(
        retrieval_hit_rate_delta=-0.10,
        groundedness_delta=-0.05,
        semantic_relevance_delta=0.10,
        overall_pass_rate_delta=-0.50,
    )

    output = format_experiment_comparison(comparison)

    assert "Retrieval delta:         -10.00%" in output
    assert "Groundedness delta:      -5.00%" in output
    assert "Semantic relevance:      +10.00%" in output
    assert "Overall pass-rate delta: -50.00%" in output
