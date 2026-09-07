from datetime import datetime

from app.schemas.evaluation import (
    EvaluationDashboardHistoryResponse,
    EvaluationHistoricalTrendResponse,
    EvaluationMetricPointResponse,
)


def test_evaluation_dashboard_history_response():
    response = EvaluationDashboardHistoryResponse(
        total_runs=3,
        passed_runs=2,
        failed_runs=1,
        pass_rate=2 / 3,
        latest_run_id=991,
        latest_quality_gate_passed=True,
        trends=[
            EvaluationHistoricalTrendResponse(
                metric_name="overall_pass_rate",
                points=[
                    EvaluationMetricPointResponse(
                        run_id=981,
                        created_at=datetime(2026, 9, 5, 17, 27, 37),
                        value=0.5,
                    ),
                    EvaluationMetricPointResponse(
                        run_id=991,
                        created_at=datetime(2026, 9, 5, 17, 40, 40),
                        value=1.0,
                    ),
                ],
                direction="improving",
            )
        ],
    )

    assert response.total_runs == 3
    assert response.passed_runs == 2
    assert response.failed_runs == 1
    assert response.pass_rate == 2 / 3
    assert response.latest_run_id == 991
    assert response.latest_quality_gate_passed is True
    assert len(response.trends) == 1
    assert response.trends[0].metric_name == "overall_pass_rate"


def test_evaluation_dashboard_history_response_with_no_runs():
    response = EvaluationDashboardHistoryResponse(
        total_runs=0,
        passed_runs=0,
        failed_runs=0,
        pass_rate=0.0,
        latest_run_id=None,
        latest_quality_gate_passed=None,
        trends=[],
    )

    assert response.total_runs == 0
    assert response.passed_runs == 0
    assert response.failed_runs == 0
    assert response.pass_rate == 0.0
    assert response.latest_run_id is None
    assert response.latest_quality_gate_passed is None
    assert response.trends == []
