from app.ai.embeddings.dependencies import (
    get_embedding_service,
)
from app.ai.evaluation.semantic_relevance_evaluator import (
    evaluate_text_relevance,
)

from tests.data.semantic_relevance_cases import (
    SEMANTIC_RELEVANCE_CASES,
)


def test_semantic_relevance_baseline():
    embedding_service = get_embedding_service()

    for case in SEMANTIC_RELEVANCE_CASES:
        result = evaluate_text_relevance(
            case["question"],
            case["answer"],
            embedding_service,
        )

        print(
            f"\nQuestion: {case['question']}"
            f"\nAnswer: {case['answer']}"
            f"\nExpected: {case['expected']}"
            f"\nScore: {result.score:.4f}"
        )

        assert 0.0 <= result.score <= 1.0
