import pytest

from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.evaluation_run import EvaluationRun


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

    assert data["runs"][1]["id"] == 1


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


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_dashboard(
    mock_repository,
):
    previous = make_evaluation_run(
        run_id=1,
    )

    latest = make_evaluation_run(
        run_id=2,
    )

    latest.average_groundedness = 0.75
    latest.average_semantic_relevance = 0.65
    latest.overall_pass_rate = 0.50

    mock_repository.return_value.get_latest_run.return_value = latest

    mock_repository.return_value.get_previous_run.return_value = previous

    response = client.get("/api/v1/evaluations/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert data["latest"]["id"] == 2
    assert data["latest"]["dataset_name"] == "rag-evaluation-v1"

    assert data["comparison"] is not None

    assert data["comparison"]["groundedness_delta"] == pytest.approx(-0.25)

    assert data["comparison"]["semantic_relevance_delta"] == pytest.approx(0.05)


@patch("app.api.evaluations.EvaluationRepository")
def test_get_evaluation_dashboard_without_history(
    mock_repository,
):
    latest = make_evaluation_run(
        run_id=10,
    )

    mock_repository.return_value.get_latest_run.return_value = latest

    mock_repository.return_value.get_previous_run.return_value = None

    response = client.get("/api/v1/evaluations/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert data["latest"]["id"] == 10
    assert data["comparison"] is None
