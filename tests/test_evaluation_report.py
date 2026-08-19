import pytest

from app.ai.evaluation.groundedness_evaluator import (
    GroundednessResult,
)

from app.ai.evaluation.rag_evaluation import (
    RAGEvaluationResult,
)

from app.ai.evaluation.semantic_relevance_evaluator import (
    SemanticRelevanceResult,
)

from app.ai.evaluation.evaluation_report import (
    build_evaluation_report,
)


def make_result(
    retrieval_hit,
    groundedness_score,
    relevance_score,
    source_count,
    overall_pass,
):
    return RAGEvaluationResult(
        retrieval_hit=retrieval_hit,
        groundedness=GroundednessResult(
            score=groundedness_score,
            supported_sentences=1,
            total_sentences=1,
        ),
        semantic_relevance=SemanticRelevanceResult(
            score=relevance_score,
        ),
        source_count=source_count,
        overall_pass=overall_pass,
    )


def test_build_evaluation_report():
    results = [
        make_result(
            True,
            1.0,
            0.8,
            2,
            True,
        ),
        make_result(
            False,
            0.5,
            0.4,
            1,
            False,
        ),
    ]

    report = build_evaluation_report(results)

    assert report.total_cases == 2

    assert report.retrieval_hit_rate == pytest.approx(0.5)

    assert report.average_groundedness == pytest.approx(0.75)

    assert report.average_semantic_relevance == pytest.approx(0.6)

    assert report.average_source_count == pytest.approx(1.5)

    assert report.overall_pass_rate == pytest.approx(0.5)


def test_build_evaluation_report_with_no_results():
    report = build_evaluation_report([])

    assert report.total_cases == 0
    assert report.retrieval_hit_rate == 0.0
    assert report.average_groundedness == 0.0
    assert report.average_semantic_relevance == 0.0
    assert report.average_source_count == 0.0
    assert report.overall_pass_rate == 0.0
