from dataclasses import dataclass

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)


@dataclass(frozen=True)
class EvaluationObservabilityEvent:
    event_name: str
    dataset_name: str
    total_cases: int
    retrieval_hit_rate: float
    average_groundedness: float
    average_semantic_relevance: float
    average_source_count: float
    overall_pass_rate: float
    quality_gate_passed: bool
    has_historical_comparison: bool

    def to_dict(self) -> dict:
        return {
            "event": self.event_name,
            "dataset": self.dataset_name,
            "total_cases": self.total_cases,
            "retrieval_hit_rate": (self.retrieval_hit_rate),
            "average_groundedness": (self.average_groundedness),
            "average_semantic_relevance": (self.average_semantic_relevance),
            "average_source_count": (self.average_source_count),
            "overall_pass_rate": (self.overall_pass_rate),
            "quality_gate_passed": (self.quality_gate_passed),
            "has_historical_comparison": (self.has_historical_comparison),
        }


def build_evaluation_event(
    snapshot: EvaluationSnapshot,
) -> EvaluationObservabilityEvent:
    return EvaluationObservabilityEvent(
        event_name="rag_evaluation_completed",
        dataset_name=snapshot.dataset_name,
        total_cases=snapshot.report.total_cases,
        retrieval_hit_rate=(snapshot.report.retrieval_hit_rate),
        average_groundedness=(snapshot.report.average_groundedness),
        average_semantic_relevance=(snapshot.report.average_semantic_relevance),
        average_source_count=(snapshot.report.average_source_count),
        overall_pass_rate=(snapshot.report.overall_pass_rate),
        quality_gate_passed=(snapshot.quality_gate.passed),
        has_historical_comparison=(snapshot.comparison is not None),
    )
