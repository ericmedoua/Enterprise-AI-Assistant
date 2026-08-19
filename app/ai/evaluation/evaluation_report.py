from dataclasses import dataclass

from app.ai.evaluation.groundedness_evaluator import (
    GroundednessResult,
)
from app.ai.evaluation.rag_evaluation import (
    RAGEvaluationResult,
)
from app.ai.evaluation.semantic_relevance_evaluator import (
    SemanticRelevanceResult,
)


@dataclass
class EvaluationReport:
    total_cases: int
    retrieval_hit_rate: float
    average_groundedness: float
    average_semantic_relevance: float
    average_source_count: float
    overall_pass_rate: float


def build_evaluation_report(
    results: list[RAGEvaluationResult],
) -> EvaluationReport:
    """
    Aggregate individual RAG evaluation results
    into a single report.
    """

    if not results:
        return EvaluationReport(
            total_cases=0,
            retrieval_hit_rate=0.0,
            average_groundedness=0.0,
            average_semantic_relevance=0.0,
            average_source_count=0.0,
            overall_pass_rate=0.0,
        )

    total_cases = len(results)

    retrieval_hit_rate = sum(result.retrieval_hit for result in results) / total_cases

    average_groundedness = (
        sum(result.groundedness.score for result in results) / total_cases
    )

    average_semantic_relevance = (
        sum(result.semantic_relevance.score for result in results) / total_cases
    )

    average_source_count = sum(result.source_count for result in results) / total_cases

    overall_pass_rate = sum(result.overall_pass for result in results) / total_cases

    return EvaluationReport(
        total_cases=total_cases,
        retrieval_hit_rate=retrieval_hit_rate,
        average_groundedness=average_groundedness,
        average_semantic_relevance=average_semantic_relevance,
        average_source_count=average_source_count,
        overall_pass_rate=overall_pass_rate,
    )
