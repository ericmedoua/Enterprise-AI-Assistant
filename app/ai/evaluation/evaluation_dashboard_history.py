from dataclasses import dataclass

from app.ai.evaluation.evaluation_historical_trends import (
    EvaluationHistoricalTrend,
)


@dataclass(frozen=True)
class EvaluationDashboardHistory:
    total_runs: int
    passed_runs: int
    failed_runs: int
    pass_rate: float
    latest_run_id: int | None
    latest_quality_gate_passed: bool | None
    trends: list[EvaluationHistoricalTrend]
