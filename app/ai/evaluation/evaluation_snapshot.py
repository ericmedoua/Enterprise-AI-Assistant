from dataclasses import dataclass

from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


@dataclass(frozen=True)
class EvaluationSnapshot:
    dataset_name: str
    report: EvaluationReport
    quality_gate: QualityGateResult
    comparison: EvaluationComparison | None

    def to_dict(self) -> dict:
        data = {
            "dataset_name": self.dataset_name,
            "report": {
                "total_cases": self.report.total_cases,
                "retrieval_hit_rate": (self.report.retrieval_hit_rate),
                "average_groundedness": (self.report.average_groundedness),
                "average_semantic_relevance": (self.report.average_semantic_relevance),
                "average_source_count": (self.report.average_source_count),
                "overall_pass_rate": (self.report.overall_pass_rate),
            },
            "quality_gate": {
                "passed": self.quality_gate.passed,
                "retrieval_passed": (self.quality_gate.retrieval_passed),
                "groundedness_passed": (self.quality_gate.groundedness_passed),
                "semantic_relevance_passed": (
                    self.quality_gate.semantic_relevance_passed
                ),
                "overall_passed": (self.quality_gate.overall_passed),
            },
            "comparison": None,
        }

        if self.comparison is not None:
            data["comparison"] = {
                "retrieval_hit_rate_delta": (self.comparison.retrieval_hit_rate_delta),
                "groundedness_delta": (self.comparison.groundedness_delta),
                "semantic_relevance_delta": (self.comparison.semantic_relevance_delta),
                "source_count_delta": (self.comparison.source_count_delta),
                "overall_pass_rate_delta": (self.comparison.overall_pass_rate_delta),
            }

        return data
