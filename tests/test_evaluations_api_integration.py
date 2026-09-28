import pytest

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

pytestmark = pytest.mark.integration


def test_evaluation_history_api_uses_database_and_pagination(
    client,
    db,
):
    repository = EvaluationRepository(db)

    first = repository.create_run(
        dataset_name="api-history-test",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.95,
        average_semantic_relevance=0.90,
        average_source_count=1.0,
        overall_pass_rate=0.90,
        quality_gate_passed=True,
    )

    second = repository.create_run(
        dataset_name="api-history-test",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        total_cases=2,
        retrieval_hit_rate=0.95,
        average_groundedness=0.85,
        average_semantic_relevance=0.80,
        average_source_count=1.0,
        overall_pass_rate=0.70,
        quality_gate_passed=True,
    )

    excluded = repository.create_run(
        dataset_name="api-history-test",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        total_cases=2,
        retrieval_hit_rate=0.90,
        average_groundedness=0.80,
        average_semantic_relevance=0.75,
        average_source_count=1.0,
        overall_pass_rate=0.60,
        quality_gate_passed=False,
    )

    db.commit()

    try:
        response = client.get(
            "/api/v1/evaluations/history",
            params={
                "dataset_name": "api-history-test",
                "quality_gate_passed": "true",
                "sort_by": "overall_pass_rate",
                "sort_order": "desc",
                "limit": 1,
                "offset": 1,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["pagination"]["total"] == 2
        assert data["pagination"]["limit"] == 1
        assert data["pagination"]["offset"] == 1
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_previous"] is True

        assert len(data["runs"]) == 1
        assert data["runs"][0]["id"] == second.id
        assert data["runs"][0]["id"] != first.id
        assert data["runs"][0]["id"] != excluded.id
        assert data["runs"][0]["quality_gate_passed"] is True

    finally:
        db.delete(first)
        db.delete(second)
        db.delete(excluded)
        db.commit()
