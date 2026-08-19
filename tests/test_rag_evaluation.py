import pytest

from app.ai.evaluation.groundedness_evaluator import (
    GroundednessResult,
)

from app.ai.evaluation.rag_evaluation import (
    evaluate_rag_response,
)

from app.ai.evaluation.semantic_relevance_evaluator import (
    SemanticRelevanceResult,
)


def test_rag_evaluation_passes_good_response():
    groundedness = GroundednessResult(
        score=1.0,
        supported_sentences=1,
        total_sentences=1,
    )

    semantic_relevance = SemanticRelevanceResult(
        score=0.68,
    )

    result = evaluate_rag_response(
        retrieval_hit=True,
        groundedness=groundedness,
        semantic_relevance=semantic_relevance,
    )

    assert result.retrieval_hit is True
    assert result.overall_pass is True


def test_rag_evaluation_fails_without_retrieval_hit():
    groundedness = GroundednessResult(
        score=1.0,
        supported_sentences=1,
        total_sentences=1,
    )

    semantic_relevance = SemanticRelevanceResult(
        score=0.68,
    )

    result = evaluate_rag_response(
        retrieval_hit=False,
        groundedness=groundedness,
        semantic_relevance=semantic_relevance,
    )

    assert result.overall_pass is False


def test_rag_evaluation_fails_when_groundedness_is_low():
    groundedness = GroundednessResult(
        score=0.5,
        supported_sentences=1,
        total_sentences=2,
    )

    semantic_relevance = SemanticRelevanceResult(
        score=0.68,
    )

    result = evaluate_rag_response(
        retrieval_hit=True,
        groundedness=groundedness,
        semantic_relevance=semantic_relevance,
    )

    assert result.overall_pass is False


def test_rag_evaluation_fails_when_semantic_relevance_is_low():
    groundedness = GroundednessResult(
        score=1.0,
        supported_sentences=1,
        total_sentences=1,
    )

    semantic_relevance = SemanticRelevanceResult(
        score=0.2294,
    )

    result = evaluate_rag_response(
        retrieval_hit=True,
        groundedness=groundedness,
        semantic_relevance=semantic_relevance,
    )

    assert result.overall_pass is False


def test_rag_evaluation_threshold_can_be_changed():
    groundedness = GroundednessResult(
        score=0.8,
        supported_sentences=4,
        total_sentences=5,
    )

    semantic_relevance = SemanticRelevanceResult(
        score=0.40,
    )

    result = evaluate_rag_response(
        retrieval_hit=True,
        groundedness=groundedness,
        semantic_relevance=semantic_relevance,
        groundedness_threshold=0.8,
        semantic_relevance_threshold=0.35,
    )

    assert result.overall_pass is True
