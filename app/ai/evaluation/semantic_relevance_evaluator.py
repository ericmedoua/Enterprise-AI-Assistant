import math
from dataclasses import dataclass


@dataclass
class SemanticRelevanceResult:
    score: float


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns a value between -1.0 and 1.0.
    """

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same dimensions.")

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))

    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def evaluate_semantic_relevance(
    question_vector: list[float],
    answer_vector: list[float],
) -> SemanticRelevanceResult:
    """
    Evaluate semantic similarity between a question
    and an answer.
    """

    score = cosine_similarity(
        question_vector,
        answer_vector,
    )

    return SemanticRelevanceResult(
        score=score,
    )


def is_semantically_relevant(
    result: SemanticRelevanceResult,
    threshold: float = 0.5,
) -> bool:
    """
    Determine whether semantic relevance meets
    the configured threshold.
    """

    return result.score >= threshold


def evaluate_text_relevance(
    question: str,
    answer: str,
    embedding_service,
) -> SemanticRelevanceResult:
    """
    Evaluate semantic relevance directly from question
    and answer text using the existing embedding service.
    """

    if not question.strip() or not answer.strip():
        return SemanticRelevanceResult(
            score=0.0,
        )

    question_vector = embedding_service.embed_query(question)

    answer_vector = embedding_service.embed_query(answer)

    return evaluate_semantic_relevance(
        question_vector,
        answer_vector,
    )
