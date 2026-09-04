import pytest

from datetime import datetime
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.evaluation_run import EvaluationRun

from datetime import datetime, timedelta, timezone


client = TestClient(app)


def make_evaluation_run(
    run_id: int = 1,
    dataset_name: str = "rag-evaluation-v1",
) -> EvaluationRun:
    return EvaluationRun(
        id=run_id,
        created_at=datetime(2026, 8, 23, 12, 0, 0),
        dataset_name=dataset_name,
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
        status="completed",
        started_at=datetime(
            2026,
            8,
            26,
            10,
            0,
            0,
        ),
        completed_at=datetime(
            2026,
            8,
            26,
            10,
            0,
            12,
        ),
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
        quality_gate_passed=True,
    )


@patch("app.api.evaluations.EvaluationRepository")
def test_get_latest_evaluation(
    mock_repository,
):
    run = make_evaluation_run()

    mock_repository.return_value.get_latest_run.return_value = run

    response = client.get("/api/v1/evaluations/latest")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["dataset_name"] == ("rag-evaluation-v1")
    assert data["status"] == "completed"
    assert data["duration_seconds"] == pytest.approx(12.0)
    assert data["llm_model"] == ("openai/gpt-oss-120b")
    assert data["embedding_model"] == ("all-MiniLM-L6-v2")
    assert data["git_commit"] == "a" * 40
    assert data["total_cases"] == 2
    assert data["retrieval_hit_rate"] == 1.0
    assert data["average_groundedness"] == 1.0
    assert data["quality_gate_passed"] is True


@patch("app.api.evaluations.EvaluationRepository")
def test_get_latest_evaluation_when_none_exist(
    mock_repository,
):
    mock_repository.return_value.get_latest_run.return_value = None

    response = client.get("/api/v1/evaluations/latest")

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "error": "No evaluation runs found.",
    }


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_history(
    mock_repository,
):
    runs = [
        make_evaluation_run(
            run_id=2,
            dataset_name="rag-evaluation-v2",
        ),
        make_evaluation_run(
            run_id=1,
            dataset_name="rag-evaluation-v1",
        ),
    ]

    mock_repository.return_value.list_runs.return_value = runs

    response = client.get("/api/v1/evaluations/history")

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data
    assert len(data["runs"]) == 2

    assert data["runs"][0]["id"] == 2
    assert data["runs"][0]["dataset_name"] == ("rag-evaluation-v2")
    assert data["runs"][0]["status"] == "completed"

    assert data["runs"][1]["id"] == 1
    assert data["runs"][1]["status"] == "completed"


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_run(
    mock_repository,
):
    run = make_evaluation_run(
        run_id=7,
    )

    mock_repository.return_value.get_run.return_value = run

    response = client.get("/api/v1/evaluations/7")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 7
    assert data["dataset_name"] == ("rag-evaluation-v1")


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_run_not_found(
    mock_repository,
):
    mock_repository.return_value.get_run.return_value = None

    response = client.get("/api/v1/evaluations/999")

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "error": "Evaluation run not found.",
    }


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_comparison(
    mock_repository,
):
    previous = make_evaluation_run(
        run_id=1,
    )

    current = make_evaluation_run(
        run_id=2,
    )

    current.average_groundedness = 0.80
    current.average_semantic_relevance = 0.65
    current.overall_pass_rate = 0.50

    mock_repository.return_value.get_run.return_value = current

    mock_repository.return_value.get_previous_run.return_value = previous

    response = client.get("/api/v1/evaluations/2/comparison")

    assert response.status_code == 200

    data = response.json()

    assert data["retrieval_hit_rate_delta"] == 0.0
    assert data["groundedness_delta"] == pytest.approx(-0.20)
    assert data["semantic_relevance_delta"] == pytest.approx(0.05)
    assert data["source_count_delta"] == 0.0
    assert data["overall_pass_rate_delta"] == pytest.approx(-0.50)


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_comparison_without_previous(
    mock_repository,
):
    current = make_evaluation_run(
        run_id=2,
    )

    mock_repository.return_value.get_run.return_value = current

    mock_repository.return_value.get_previous_run.return_value = None

    response = client.get("/api/v1/evaluations/2/comparison")

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "error": "No previous evaluation run found.",
    }


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_comparison_run_not_found(
    mock_repository,
):
    mock_repository.return_value.get_run.return_value = None

    response = client.get("/api/v1/evaluations/999/comparison")

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "error": "Evaluation run not found.",
    }


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_snapshot(
    mock_repository,
):
    previous = make_evaluation_run(
        run_id=1,
    )

    current = make_evaluation_run(
        run_id=2,
    )

    current.average_groundedness = 0.75
    current.average_semantic_relevance = 0.65

    mock_repository.return_value.get_run.return_value = current

    mock_repository.return_value.get_previous_run.return_value = previous

    response = client.get("/api/v1/evaluations/2/snapshot")

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_name"] == ("rag-evaluation-v1")

    assert data["report"]["total_cases"] == 2

    assert data["quality_gate"]["passed"] is True

    assert data["comparison"]["groundedness_delta"] == pytest.approx(-0.25)


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_snapshot_without_history(
    mock_repository,
):
    current = make_evaluation_run(
        run_id=10,
    )

    mock_repository.return_value.get_run.return_value = current

    mock_repository.return_value.get_previous_run.return_value = None

    response = client.get("/api/v1/evaluations/10/snapshot")

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_name"] == ("rag-evaluation-v1")

    assert data["comparison"] is None


@patch("app.api.evaluations.build_evaluation_dashboard")
def test_get_evaluation_dashboard(
    mock_build_dashboard,
):
    latest = make_evaluation_run(
        run_id=2,
    )

    comparison = Mock(
        retrieval_hit_rate_delta=0.0,
        groundedness_delta=-0.25,
        semantic_relevance_delta=0.05,
        source_count_delta=0.0,
        overall_pass_rate_delta=-0.5,
    )

    quality_health = Mock(
        healthy=False,
        status="degraded",
        latest_run_id=2,
        quality_gate_passed=False,
        trend_status="declining",
    )

    operational_health = Mock(
        healthy=True,
        running_count=0,
        stale_count=0,
        cancelled_count=0,
    )

    mock_build_dashboard.return_value = Mock(
        latest=latest,
        comparison=comparison,
        quality_health=quality_health,
        operational_health=operational_health,
    )

    response = client.get("/api/v1/evaluations/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert data["latest"]["id"] == 2

    assert data["comparison"] is not None
    assert data["comparison"]["groundedness_delta"] == pytest.approx(-0.25)
    assert data["comparison"]["semantic_relevance_delta"] == pytest.approx(0.05)

    assert data["quality_health"]["healthy"] is False
    assert data["quality_health"]["status"] == "degraded"
    assert data["quality_health"]["latest_run_id"] == 2
    assert data["quality_health"]["quality_gate_passed"] is False
    assert data["quality_health"]["trend_status"] == "declining"

    assert data["operational_health"]["healthy"] is True
    assert data["operational_health"]["running_count"] == 0
    assert data["operational_health"]["stale_count"] == 0
    assert data["operational_health"]["cancelled_count"] == 0

    mock_build_dashboard.assert_called_once()


@patch("app.api.evaluations.build_evaluation_dashboard")
def test_get_evaluation_dashboard_without_history(
    mock_build_dashboard,
):
    mock_build_dashboard.side_effect = ValueError("No evaluation runs found.")

    response = client.get("/api/v1/evaluations/dashboard")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == "No evaluation runs found."

    mock_build_dashboard.assert_called_once()


@patch("app.api.evaluations.get_evaluation_metadata")
@patch("app.api.evaluations.EvaluationRunner")
def test_start_evaluation_run(
    mock_runner,
    mock_metadata,
):
    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    queued_run = Mock(
        id=42,
        status="queued",
    )

    mock_metadata.return_value = metadata
    mock_runner.return_value.create_run.return_value = queued_run

    response = client.post("/api/v1/evaluations/run")

    assert response.status_code == 202

    data = response.json()

    assert data["evaluation_run_id"] == 42
    assert data["status"] == "queued"

    assert mock_runner.call_count == 2

    mock_runner.return_value.create_run.assert_called_once()

    mock_runner.return_value.execute_run.assert_called_once_with(42)


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_run_status(
    mock_repository,
):
    run = make_evaluation_run(
        run_id=25,
    )

    run.status = "failed"

    mock_repository.return_value.get_run.return_value = run

    response = client.get("/api/v1/evaluations/25")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 25
    assert data["status"] == "failed"


@patch("app.api.evaluations.app_logger")
@patch("app.api.evaluations.get_evaluation_metadata")
@patch("app.api.evaluations.EvaluationRunner")
def test_start_evaluation_run_failure(
    mock_runner,
    mock_metadata,
    mock_logger,
):
    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    queued_run = Mock(
        id=42,
        status="queued",
    )

    mock_metadata.return_value = metadata

    mock_runner.return_value.create_run.return_value = queued_run

    mock_runner.return_value.execute_run.side_effect = RuntimeError("benchmark failed")

    response = client.post("/api/v1/evaluations/run")

    assert response.status_code == 202

    data = response.json()

    assert data["evaluation_run_id"] == 42
    assert data["status"] == "queued"

    mock_runner.return_value.execute_run.assert_called_once_with(42)

    mock_logger.exception.assert_called_once()


@patch("app.api.evaluations.get_evaluation_metadata")
@patch("app.api.evaluations.EvaluationRunner")
@patch("app.api.evaluations.SessionLocal")
def test_execute_evaluation_in_background(
    mock_session_local,
    mock_runner,
    mock_metadata,
):
    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    db = Mock()

    mock_session_local.return_value = db
    mock_metadata.return_value = metadata

    from app.api.evaluations import (
        _execute_evaluation_in_background,
    )

    _execute_evaluation_in_background(42)

    mock_runner.assert_called_once_with(
        db=db,
        metadata=metadata,
    )

    mock_runner.return_value.execute_run.assert_called_once_with(42)

    db.close.assert_called_once()


@patch("app.api.evaluations.get_evaluation_metadata")
@patch("app.api.evaluations.EvaluationRunner")
@patch("app.api.evaluations.SessionLocal")
@patch("app.api.evaluations.app_logger")
def test_execute_evaluation_in_background_closes_session_on_failure(
    mock_logger,
    mock_session_local,
    mock_runner,
    mock_metadata,
):
    metadata = Mock(
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="a" * 40,
    )

    db = Mock()

    mock_session_local.return_value = db
    mock_metadata.return_value = metadata

    mock_runner.return_value.execute_run.side_effect = RuntimeError("benchmark failed")

    from app.api.evaluations import (
        _execute_evaluation_in_background,
    )

    _execute_evaluation_in_background(42)

    mock_runner.assert_called_once_with(
        db=db,
        metadata=metadata,
    )

    mock_runner.return_value.execute_run.assert_called_once_with(42)

    mock_logger.exception.assert_called_once()
    db.close.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_run_without_duration(
    mock_repository,
):
    run = make_evaluation_run(
        run_id=30,
    )

    run.status = "running"
    run.started_at = datetime(
        2026,
        8,
        26,
        10,
        0,
        0,
    )
    run.completed_at = None

    mock_repository.return_value.get_run.return_value = run

    response = client.get("/api/v1/evaluations/30")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["duration_seconds"] is None


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_health(
    mock_repository,
):
    running_run = Mock(
        status="running",
        started_at=datetime.now(timezone.utc),
    )

    mock_repository.return_value.list_running_runs.return_value = [running_run]

    mock_repository.return_value.count_cancelled_runs.return_value = 2

    response = client.get("/api/v1/evaluations/health")

    assert response.status_code == 200

    data = response.json()

    assert data["healthy"] is True
    assert data["running_count"] == 1
    assert data["stale_count"] == 0
    assert data["cancelled_count"] == 2


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_health_without_running_runs(
    mock_repository,
):
    mock_repository.return_value.list_running_runs.return_value = []
    mock_repository.return_value.count_cancelled_runs.return_value = 0

    response = client.get("/api/v1/evaluations/health")

    assert response.status_code == 200

    data = response.json()

    assert data["healthy"] is True
    assert data["running_count"] == 0
    assert data["stale_count"] == 0
    assert data["cancelled_count"] == 0


@patch(
    "app.api.evaluations.is_evaluation_stale",
)
@patch(
    "app.api.evaluations.EvaluationRepository",
)
def test_get_stale_evaluations(
    mock_repository,
    mock_is_stale,
):
    stale_run = Mock(
        id=25,
        dataset_name="rag-evaluation-v1",
        status="running",
        started_at=datetime.now(timezone.utc),
    )

    mock_repository.return_value.list_running_runs.return_value = [stale_run]

    mock_is_stale.return_value = True

    response = client.get("/api/v1/evaluations/stale")

    assert response.status_code == 200

    data = response.json()

    assert len(data["runs"]) == 1
    assert data["runs"][0]["id"] == 25
    assert data["runs"][0]["status"] == "running"
    assert data["runs"][0]["dataset_name"] == ("rag-evaluation-v1")

    assert data["runs"][0]["duration_seconds"] >= 0

    mock_is_stale.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_stale_evaluations_when_none_exist(
    mock_repository,
):
    mock_repository.return_value.list_running_runs.return_value = []

    response = client.get("/api/v1/evaluations/stale")

    assert response.status_code == 200

    data = response.json()

    assert data["runs"] == []


@patch("app.api.evaluations.EvaluationRepository")
def test_fail_stale_evaluation(
    mock_repository,
):
    stale_run = make_evaluation_run(
        run_id=25,
    )

    stale_run.status = "failed"

    mock_repository.return_value.get_run.return_value = stale_run

    mock_repository.return_value.fail_stale_run.return_value = stale_run

    response = client.post("/api/v1/evaluations/25/fail")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 25
    assert data["status"] == "failed"

    mock_repository.return_value.fail_stale_run.assert_called_once_with(
        run_id=25,
    )


@patch("app.api.evaluations.EvaluationRepository")
def test_fail_stale_evaluation_not_found(
    mock_repository,
):
    mock_repository.return_value.get_run.return_value = None

    response = client.post("/api/v1/evaluations/999/fail")

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "error": "Evaluation run not found.",
    }

    mock_repository.return_value.fail_stale_run.assert_not_called()


@patch("app.api.evaluations.EvaluationRepository")
def test_fail_stale_evaluation_conflict(
    mock_repository,
):
    current_run = make_evaluation_run(
        run_id=30,
    )

    current_run.status = "running"

    mock_repository.return_value.get_run.return_value = current_run

    mock_repository.return_value.fail_stale_run.return_value = None

    response = client.post("/api/v1/evaluations/30/fail")

    assert response.status_code == 409

    assert response.json() == {
        "success": False,
        "error": ("Evaluation run is not stale or cannot be remediated."),
    }


@patch("app.api.evaluations.EvaluationRepository")
def test_cancel_queued_evaluation(
    mock_repository,
):
    queued_run = make_evaluation_run(
        run_id=60,
    )

    queued_run.status = "cancelled"
    queued_run.completed_at = datetime.now()

    mock_repository.return_value.get_run.return_value = queued_run

    mock_repository.return_value.cancel_queued_run.return_value = queued_run

    response = client.post("/api/v1/evaluations/60/cancel")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 60
    assert data["status"] == "cancelled"

    mock_repository.return_value.cancel_queued_run.assert_called_once_with(
        run_id=60,
    )


@patch("app.api.evaluations.EvaluationRepository")
def test_cancel_evaluation_not_found(
    mock_repository,
):
    mock_repository.return_value.get_run.return_value = None

    response = client.post("/api/v1/evaluations/9999/cancel")

    assert response.status_code == 404

    assert response.json() == {
        "success": False,
        "error": "Evaluation run not found.",
    }

    mock_repository.return_value.cancel_queued_run.assert_not_called()


@patch("app.api.evaluations.EvaluationRepository")
def test_cancel_running_evaluation(
    mock_repository,
):
    running_run = make_evaluation_run(
        run_id=61,
    )

    running_run.status = "running"

    mock_repository.return_value.get_run.return_value = running_run

    mock_repository.return_value.cancel_queued_run.return_value = None

    response = client.post("/api/v1/evaluations/61/cancel")

    assert response.status_code == 409

    assert response.json() == {
        "success": False,
        "error": ("Evaluation run cannot be cancelled because it is not queued."),
    }


@patch("app.api.evaluations.EvaluationRepository")
def test_get_latest_evaluation_observability(
    mock_repository,
):
    run = make_evaluation_run(
        run_id=408,
    )

    run.status = "completed"

    run.started_at = datetime(
        2026,
        8,
        30,
        13,
        0,
        0,
    )

    run.completed_at = datetime(
        2026,
        8,
        30,
        13,
        0,
        10,
    )

    mock_repository.return_value.get_latest_run.return_value = run

    response = client.get("/api/v1/evaluations/observability/latest")

    assert response.status_code == 200

    data = response.json()

    assert data["event"] == ("rag_evaluation_completed")
    assert data["dataset"] == ("rag-evaluation-v1")
    assert data["total_cases"] == 2
    assert data["retrieval_hit_rate"] == 1.0
    assert data["average_groundedness"] == 1.0
    assert data["average_semantic_relevance"] == 0.60
    assert data["average_source_count"] == 1.0
    assert data["overall_pass_rate"] == 1.0
    assert data["quality_gate_passed"] is True
    assert data["status"] == "completed"
    assert data["duration_seconds"] == pytest.approx(10.0)


@patch("app.api.evaluations.EvaluationRepository")
def test_get_latest_evaluation_observability_when_none_exist(
    mock_repository,
):
    mock_repository.return_value.get_latest_run.return_value = None

    response = client.get("/api/v1/evaluations/observability/latest")

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["error"] == ("No evaluation runs found.")


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_observability_history(
    mock_repository,
):
    runs = [
        make_evaluation_run(
            run_id=2,
        ),
        make_evaluation_run(
            run_id=1,
        ),
    ]

    mock_repository.return_value.list_runs.return_value = runs

    response = client.get("/api/v1/evaluations/observability/history")

    assert response.status_code == 200

    data = response.json()

    assert "runs" in data
    assert len(data["runs"]) == 2

    assert data["runs"][0]["id"] == 2
    assert data["runs"][1]["id"] == 1

    assert data["runs"][0]["dataset_name"] == "rag-evaluation-v1"

    assert data["runs"][0]["duration_seconds"] is not None

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_observability_history_empty(
    mock_repository,
):
    mock_repository.return_value.list_runs.return_value = []

    response = client.get("/api/v1/evaluations/observability/history")

    assert response.status_code == 200

    data = response.json()

    assert data["runs"] == []

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_trends(mock_repository):
    previous = Mock(
        id=1,
        retrieval_hit_rate=0.8,
        average_groundedness=0.8,
        average_semantic_relevance=0.7,
        average_source_count=1.0,
        overall_pass_rate=0.5,
    )

    current = Mock(
        id=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        average_source_count=2.0,
        overall_pass_rate=1.0,
    )

    mock_repository.return_value.list_runs.return_value = [
        current,
        previous,
    ]

    response = client.get("/api/v1/evaluations/trends")

    assert response.status_code == 200

    data = response.json()

    assert "trends" in data
    assert len(data["trends"]) == 5

    assert data["trends"][0]["metric_name"] == ("retrieval_hit_rate")
    assert data["trends"][0]["previous_value"] == 0.8
    assert data["trends"][0]["current_value"] == 1.0
    assert data["trends"][0]["delta"] == pytest.approx(0.2)
    assert data["trends"][0]["direction"] == "improving"

    assert data["trends"][1]["metric_name"] == ("average_groundedness")
    assert data["trends"][1]["direction"] == "improving"

    assert data["trends"][2]["metric_name"] == ("average_semantic_relevance")
    assert data["trends"][2]["direction"] == "improving"

    assert data["trends"][3]["metric_name"] == ("average_source_count")
    assert data["trends"][3]["direction"] == "improving"

    assert data["trends"][4]["metric_name"] == ("overall_pass_rate")
    assert data["trends"][4]["direction"] == "improving"

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_trends_with_insufficient_history(
    mock_repository,
):
    mock_repository.return_value.list_runs.return_value = [
        make_evaluation_run(run_id=1),
    ]

    response = client.get("/api/v1/evaluations/trends")

    assert response.status_code == 200

    data = response.json()

    assert data["trends"] == []

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_trends_stable(mock_repository):
    previous = Mock(
        id=1,
        retrieval_hit_rate=0.8000,
        average_groundedness=0.9000,
        average_semantic_relevance=0.7000,
        average_source_count=1.0000,
        overall_pass_rate=0.8000,
    )

    current = Mock(
        id=2,
        retrieval_hit_rate=0.8005,
        average_groundedness=0.9005,
        average_semantic_relevance=0.7005,
        average_source_count=1.0005,
        overall_pass_rate=0.8005,
    )

    mock_repository.return_value.list_runs.return_value = [
        current,
        previous,
    ]

    response = client.get("/api/v1/evaluations/trends")

    assert response.status_code == 200

    data = response.json()

    assert len(data["trends"]) == 5

    assert all(trend["direction"] == "stable" for trend in data["trends"])


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_trends_declining(mock_repository):
    previous = Mock(
        id=1,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.9,
        average_source_count=2.0,
        overall_pass_rate=1.0,
    )

    current = Mock(
        id=2,
        retrieval_hit_rate=0.8,
        average_groundedness=0.7,
        average_semantic_relevance=0.6,
        average_source_count=1.0,
        overall_pass_rate=0.5,
    )

    mock_repository.return_value.list_runs.return_value = [
        current,
        previous,
    ]

    response = client.get("/api/v1/evaluations/trends")

    assert response.status_code == 200

    data = response.json()

    assert len(data["trends"]) == 5

    assert all(trend["direction"] == "declining" for trend in data["trends"])


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_trends_empty_history(mock_repository):
    mock_repository.return_value.list_runs.return_value = []

    response = client.get("/api/v1/evaluations/trends")

    assert response.status_code == 200

    data = response.json()

    assert data["trends"] == []

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_historical_trends(mock_repository):
    older = Mock(
        id=1,
        created_at=datetime(
            2026,
            8,
            1,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=0.8,
        average_groundedness=0.8,
        average_semantic_relevance=0.7,
        average_source_count=1.0,
        overall_pass_rate=0.5,
    )

    newer = Mock(
        id=2,
        created_at=datetime(
            2026,
            8,
            2,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        average_source_count=2.0,
        overall_pass_rate=1.0,
    )

    mock_repository.return_value.list_runs.return_value = [
        newer,
        older,
    ]

    response = client.get("/api/v1/evaluations/historical-trends")

    assert response.status_code == 200

    data = response.json()

    assert "trends" in data
    assert len(data["trends"]) == 5

    retrieval = data["trends"][0]

    assert retrieval["metric_name"] == ("retrieval_hit_rate")
    assert retrieval["direction"] == "improving"

    assert len(retrieval["points"]) == 2

    assert retrieval["points"][0]["run_id"] == 1
    assert retrieval["points"][0]["value"] == 0.8

    assert retrieval["points"][1]["run_id"] == 2
    assert retrieval["points"][1]["value"] == 1.0

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_historical_trends_empty(
    mock_repository,
):
    mock_repository.return_value.list_runs.return_value = []

    response = client.get("/api/v1/evaluations/historical-trends")

    assert response.status_code == 200

    data = response.json()

    assert len(data["trends"]) == 5

    assert all(trend["points"] == [] for trend in data["trends"])

    assert all(trend["direction"] == "stable" for trend in data["trends"])

    mock_repository.return_value.list_runs.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_historical_trends_with_limit(
    mock_repository,
):
    mock_repository.return_value.list_runs.return_value = []

    response = client.get("/api/v1/evaluations/historical-trends?limit=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data["trends"]) == 5

    mock_repository.return_value.list_runs.assert_called_once_with(
        limit=10,
    )


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_historical_trends_invalid_limit(
    mock_repository,
):
    response = client.get("/api/v1/evaluations/historical-trends?limit=0")

    assert response.status_code == 422

    mock_repository.return_value.list_runs.assert_not_called()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_historical_trends_negative_limit(
    mock_repository,
):
    response = client.get("/api/v1/evaluations/historical-trends?limit=-5")

    assert response.status_code == 422

    mock_repository.return_value.list_runs.assert_not_called()


@patch("app.api.evaluations.EvaluationRepository")
@patch("app.api.evaluations.build_evaluation_quality_health")
def test_get_evaluation_quality_health(
    mock_build_health,
    mock_repository,
):
    mock_build_health.return_value = Mock(
        healthy=True,
        status="healthy",
        latest_run_id=100,
        quality_gate_passed=True,
        trend_status="stable",
    )

    response = client.get("/api/v1/evaluations/quality-health")

    assert response.status_code == 200

    data = response.json()

    assert data["healthy"] is True
    assert data["status"] == "healthy"
    assert data["latest_run_id"] == 100
    assert data["quality_gate_passed"] is True
    assert data["trend_status"] == "stable"

    mock_build_health.assert_called_once()

    mock_repository.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_quality_health_no_runs(
    mock_repository,
):
    mock_repository.return_value.get_latest_run.return_value = None

    response = client.get("/api/v1/evaluations/quality-health")

    assert response.status_code == 200

    data = response.json()

    assert data["healthy"] is False
    assert data["status"] == "unhealthy"
    assert data["latest_run_id"] is None
    assert data["quality_gate_passed"] is False
    assert data["trend_status"] == "stable"

    mock_repository.return_value.get_latest_run.assert_called_once()


@patch("app.api.evaluations.EvaluationRepository")
@patch("app.api.evaluations.build_evaluation_quality_health")
def test_get_evaluation_quality_health_quality_gate_failed(
    mock_build_health,
    mock_repository,
):
    mock_build_health.return_value = Mock(
        healthy=False,
        status="degraded",
        latest_run_id=100,
        quality_gate_passed=False,
        trend_status="stable",
    )

    response = client.get("/api/v1/evaluations/quality-health")

    assert response.status_code == 200

    data = response.json()

    assert data["healthy"] is False
    assert data["status"] == "degraded"
    assert data["latest_run_id"] == 100
    assert data["quality_gate_passed"] is False
    assert data["trend_status"] == "stable"

    mock_build_health.assert_called_once()

    mock_repository.assert_called_once()


@patch("app.api.evaluations.build_evaluation_dashboard")
def test_get_evaluation_dashboard_with_operational_degradation(
    mock_build_dashboard,
):
    latest = make_evaluation_run(
        run_id=20,
    )

    comparison = Mock(
        retrieval_hit_rate_delta=0.0,
        groundedness_delta=0.0,
        semantic_relevance_delta=0.0,
        source_count_delta=0.0,
        overall_pass_rate_delta=0.0,
    )

    quality_health = Mock(
        healthy=True,
        status="healthy",
        latest_run_id=20,
        quality_gate_passed=True,
        trend_status="stable",
    )

    operational_health = Mock(
        healthy=False,
        running_count=2,
        stale_count=1,
        cancelled_count=3,
    )

    mock_build_dashboard.return_value = Mock(
        latest=latest,
        comparison=comparison,
        quality_health=quality_health,
        operational_health=operational_health,
    )

    response = client.get("/api/v1/evaluations/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert data["latest"]["id"] == 20

    assert data["quality_health"]["healthy"] is True
    assert data["quality_health"]["status"] == "healthy"

    assert data["operational_health"]["healthy"] is False
    assert data["operational_health"]["running_count"] == 2
    assert data["operational_health"]["stale_count"] == 1
    assert data["operational_health"]["cancelled_count"] == 3

    mock_build_dashboard.assert_called_once()
