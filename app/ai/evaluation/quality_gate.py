from dataclasses import dataclass

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)


@dataclass(frozen=True)
class QualityThresholds:
    minimum_retrieval_hit_rate: float = 1.0
    minimum_groundedness: float = 0.90
    minimum_semantic_relevance: float = 0.50
    minimum_overall_pass_rate: float = 1.0


@dataclass(frozen=True)
class QualityGateFailure:
    metric_name: str
    actual_value: float
    required_value: float


@dataclass(frozen=True)
class QualityGateResult:
    passed: bool
    retrieval_passed: bool
    groundedness_passed: bool
    semantic_relevance_passed: bool
    overall_passed: bool
    failures: tuple[QualityGateFailure, ...] = ()


def evaluate_quality_gate(
    report: EvaluationReport,
    thresholds: QualityThresholds | None = None,
) -> QualityGateResult:
    if thresholds is None:
        thresholds = QualityThresholds()

    retrieval_passed = (
        report.retrieval_hit_rate >= thresholds.minimum_retrieval_hit_rate
    )

    groundedness_passed = report.average_groundedness >= thresholds.minimum_groundedness

    semantic_relevance_passed = (
        report.average_semantic_relevance >= thresholds.minimum_semantic_relevance
    )

    overall_passed = report.overall_pass_rate >= thresholds.minimum_overall_pass_rate

    failures = []

    if not retrieval_passed:
        failures.append(
            QualityGateFailure(
                metric_name="retrieval_hit_rate",
                actual_value=report.retrieval_hit_rate,
                required_value=thresholds.minimum_retrieval_hit_rate,
            )
        )

    if not groundedness_passed:
        failures.append(
            QualityGateFailure(
                metric_name="average_groundedness",
                actual_value=report.average_groundedness,
                required_value=thresholds.minimum_groundedness,
            )
        )

    if not semantic_relevance_passed:
        failures.append(
            QualityGateFailure(
                metric_name="average_semantic_relevance",
                actual_value=report.average_semantic_relevance,
                required_value=thresholds.minimum_semantic_relevance,
            )
        )

    if not overall_passed:
        failures.append(
            QualityGateFailure(
                metric_name="overall_pass_rate",
                actual_value=report.overall_pass_rate,
                required_value=thresholds.minimum_overall_pass_rate,
            )
        )

    passed = not failures

    return QualityGateResult(
        passed=passed,
        retrieval_passed=retrieval_passed,
        groundedness_passed=groundedness_passed,
        semantic_relevance_passed=semantic_relevance_passed,
        overall_passed=overall_passed,
        failures=tuple(failures),
    )
