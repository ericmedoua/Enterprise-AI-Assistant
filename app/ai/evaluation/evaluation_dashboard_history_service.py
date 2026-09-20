from app.ai.evaluation.evaluation_dashboard_history import (
    EvaluationDashboardHistory,
)
from app.ai.evaluation.evaluation_historical_trend_service import (
    build_evaluation_historical_trends_from_runs,
)


def build_evaluation_dashboard_history(repository, limit: int | None = None):
    runs = repository.list_runs(limit=limit)

    if not runs:
        return EvaluationDashboardHistory(
            total_runs=0,
            passed_runs=0,
            failed_runs=0,
            pass_rate=0.0,
            latest_run_id=None,
            latest_quality_gate_passed=None,
            trends=build_evaluation_historical_trends_from_runs(
                runs,
            ),
        )

    passed_runs = sum(1 for run in runs if run.quality_gate_passed)

    failed_runs = len(runs) - passed_runs
    pass_rate = passed_runs / len(runs)

    latest_run = runs[0]

    trends = build_evaluation_historical_trends_from_runs(
        runs,
    )

    return EvaluationDashboardHistory(
        total_runs=len(runs),
        passed_runs=passed_runs,
        failed_runs=failed_runs,
        pass_rate=pass_rate,
        latest_run_id=latest_run.id,
        latest_quality_gate_passed=latest_run.quality_gate_passed,
        trends=trends,
    )
