from unittest.mock import Mock

from app.ai.evaluation.evaluation_dashboard_history import (
    EvaluationDashboardHistory,
)


def test_evaluation_dashboard_history_creation():
    trend = Mock()

    history = EvaluationDashboardHistory(
        total_runs=3,
        passed_runs=2,
        failed_runs=1,
        pass_rate=2 / 3,
        latest_run_id=991,
        latest_quality_gate_passed=True,
        trends=[trend],
    )

    assert history.total_runs == 3
    assert history.passed_runs == 2
    assert history.failed_runs == 1
    assert history.pass_rate == 2 / 3
    assert history.latest_run_id == 991
    assert history.latest_quality_gate_passed is True
    assert history.trends == [trend]


def test_evaluation_dashboard_history_supports_empty_history():
    history = EvaluationDashboardHistory(
        total_runs=0,
        passed_runs=0,
        failed_runs=0,
        pass_rate=0.0,
        latest_run_id=None,
        latest_quality_gate_passed=None,
        trends=[],
    )

    assert history.total_runs == 0
    assert history.passed_runs == 0
    assert history.failed_runs == 0
    assert history.pass_rate == 0.0
    assert history.latest_run_id is None
    assert history.latest_quality_gate_passed is None
    assert history.trends == []
