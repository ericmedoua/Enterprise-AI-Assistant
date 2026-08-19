import pytest
from unittest.mock import Mock

from app.ai.evaluation.semantic_relevance_evaluator import (
    cosine_similarity,
    evaluate_semantic_relevance,
    is_semantically_relevant,
    evaluate_text_relevance,
)


def test_identical_vectors_have_similarity_of_one():
    assert cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    ) == pytest.approx(1.0)


def test_orthogonal_vectors_have_similarity_of_zero():
    assert cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    ) == pytest.approx(0.0)


def test_empty_vector_returns_zero():
    assert (
        cosine_similarity(
            [],
            [1.0, 0.0],
        )
        == 0.0
    )


def test_different_dimensions_raise_error():
    with pytest.raises(ValueError):
        cosine_similarity(
            [1.0, 0.0],
            [1.0],
        )


def test_semantic_relevance_result():
    result = evaluate_semantic_relevance(
        [1.0, 0.0],
        [1.0, 0.0],
    )

    assert result.score == pytest.approx(1.0)


def test_semantically_relevant_threshold():
    result = evaluate_semantic_relevance(
        [1.0, 0.0],
        [1.0, 0.0],
    )

    assert (
        is_semantically_relevant(
            result,
            threshold=0.8,
        )
        is True
    )


def test_not_semantically_relevant_threshold():
    result = evaluate_semantic_relevance(
        [1.0, 0.0],
        [0.0, 1.0],
    )

    assert (
        is_semantically_relevant(
            result,
            threshold=0.8,
        )
        is False
    )


def test_evaluate_text_relevance_uses_embedding_service():
    embedding_service = Mock()

    embedding_service.embed_query.side_effect = [
        [1.0, 0.0],
        [1.0, 0.0],
    ]

    result = evaluate_text_relevance(
        "What do monkeys do?",
        "Monkeys swing from trees.",
        embedding_service,
    )

    assert result.score == pytest.approx(1.0)

    assert embedding_service.embed_query.call_count == 2


def test_evaluate_text_relevance_handles_empty_input():
    embedding_service = Mock()

    result = evaluate_text_relevance(
        "",
        "Monkeys swing from trees.",
        embedding_service,
    )

    assert result.score == 0.0

    embedding_service.embed_query.assert_not_called()
