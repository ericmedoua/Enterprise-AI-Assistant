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
    source_count: int
    overall_pass: bool

    def summary(self) -> dict:
        """
        Return a compact, report-friendly representation
        of the evaluation result.
        """
        return {
        "retrieval_hit": self.retrieval_hit,
        "groundedness_score": self.groundedness.score,
        "semantic_relevance_score": (self.semantic_relevance.score),
        "source_count": self.source_count,
        "overall_pass": self.overall_pass,
    }


def evaluate_rag_response(
    retrieval_hit: bool,
    groundedness: GroundednessResult,
    semantic_relevance: SemanticRelevanceResult,
    source_count: int,
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
        source_count=source_count,
        overall_pass=overall_pass,
    )



