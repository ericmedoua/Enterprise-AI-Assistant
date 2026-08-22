import pytest

from app.ai.evaluation.evaluation_comparator import (
    compare_evaluation_runs,
)

from app.models.evaluation_run import EvaluationRun


def make_run(
    retrieval=1.0,
    groundedness=1.0,
    relevance=0.60,
    source_count=1.0,
    overall=1.0,
):
    return EvaluationRun(
        id=1,
        dataset_name="rag-evaluation-v1",
        total_cases=2,
        retrieval_hit_rate=retrieval,
        average_groundedness=groundedness,
        average_semantic_relevance=relevance,
        average_source_count=source_count,
        overall_pass_rate=overall,
        quality_gate_passed=True,
    )


def test_compare_evaluation_runs():
    previous = make_run(
        retrieval=1.0,
        groundedness=1.0,
        relevance=0.60,
        source_count=1.0,
        overall=1.0,
    )

    current = make_run(
        retrieval=0.90,
        groundedness=0.80,
        relevance=0.65,
        source_count=1.5,
        overall=0.50,
    )

    comparison = compare_evaluation_runs(
        previous,
        current,
    )

    assert comparison.retrieval_hit_rate_delta == pytest.approx(-0.10)

    assert comparison.groundedness_delta == pytest.approx(-0.20)

    assert comparison.semantic_relevance_delta == pytest.approx(0.05)

    assert comparison.source_count_delta == pytest.approx(0.50)

    assert comparison.overall_pass_rate_delta == pytest.approx(-0.50)


def test_identical_runs_have_zero_delta():
    previous = make_run()
    current = make_run()

    comparison = compare_evaluation_runs(
        previous,
        current,
    )

    assert comparison.retrieval_hit_rate_delta == 0.0
    assert comparison.groundedness_delta == 0.0
    assert comparison.semantic_relevance_delta == 0.0
    assert comparison.source_count_delta == 0.0
    assert comparison.overall_pass_rate_delta == 0.0
