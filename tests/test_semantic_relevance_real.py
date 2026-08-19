from app.ai.embeddings.dependencies import (
    get_embedding_service,
)
from app.ai.evaluation.semantic_relevance_evaluator import (
    evaluate_text_relevance,
)


def test_real_semantic_relevance():
    embedding_service = get_embedding_service()

    result = evaluate_text_relevance(
        "What do monkeys do?",
        "Monkeys swing from trees and love bananas.",
        embedding_service,
    )

    print(f"\nSemantic relevance score: {result.score:.4f}")

    assert 0.0 <= result.score <= 1.0


def test_real_semantic_relevance_for_unrelated_answer():
    embedding_service = get_embedding_service()

    result = evaluate_text_relevance(
        "What do monkeys do?",
        "Reindeer have antlers and pull sleds.",
        embedding_service,
    )

    print(f"\nUnrelated semantic relevance score: {result.score:.4f}")

    assert 0.0 <= result.score <= 1.0
