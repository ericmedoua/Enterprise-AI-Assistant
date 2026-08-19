from dataclasses import dataclass

from app.ai.evaluation.groundedness_evaluator import (
    GroundednessResult,
)
from app.ai.evaluation.semantic_relevance_evaluator import (
    SemanticRelevanceResult,
)


@dataclass
class RAGEvaluationResult:
    retrieval_hit: bool
    groundedness: GroundednessResult
    semantic_relevance: SemanticRelevanceResult
    overall_pass: bool


def evaluate_rag_response(
    retrieval_hit: bool,
    groundedness: GroundednessResult,
    semantic_relevance: SemanticRelevanceResult,
    groundedness_threshold: float = 1.0,
    semantic_relevance_threshold: float = 0.35,
) -> RAGEvaluationResult:
    """
    Combine independent RAG evaluation metrics
    into a single result.
    """

    grounded = groundedness.score >= groundedness_threshold

    semantically_relevant = semantic_relevance.score >= semantic_relevance_threshold

    overall_pass = retrieval_hit and grounded and semantically_relevant

    return RAGEvaluationResult(
        retrieval_hit=retrieval_hit,
        groundedness=groundedness,
        semantic_relevance=semantic_relevance,
        overall_pass=overall_pass,
    )
