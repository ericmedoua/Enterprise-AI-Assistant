import pytest

from app.ai.evaluation.experiment_comparator import (
    compare_experiments,
)

from app.models.evaluation_run import EvaluationRun


def make_run(
    retrieval,
    groundedness,
    relevance,
    overall,
):
    return EvaluationRun(
        id=1,
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test",
        total_cases=2,
        retrieval_hit_rate=retrieval,
        average_groundedness=groundedness,
        average_semantic_relevance=relevance,
        average_source_count=1.0,
        overall_pass_rate=overall,
        quality_gate_passed=True,
    )


def test_compare_experiments():
    baseline = make_run(
        1.0,
        1.0,
        0.60,
        1.0,
    )

    candidate = make_run(
        0.90,
        0.95,
        0.70,
        0.50,
    )

    result = compare_experiments(
        baseline,
        candidate,
    )

    assert result.retrieval_hit_rate_delta == pytest.approx(-0.10)

    assert result.groundedness_delta == pytest.approx(-0.05)

    assert result.semantic_relevance_delta == pytest.approx(0.10)

    assert result.overall_pass_rate_delta == pytest.approx(-0.50)
