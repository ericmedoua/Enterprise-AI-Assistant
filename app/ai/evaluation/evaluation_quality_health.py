from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationQualityHealth:
    healthy: bool
    status: str
    latest_run_id: int | None
    quality_gate_passed: bool
    trend_status: str
