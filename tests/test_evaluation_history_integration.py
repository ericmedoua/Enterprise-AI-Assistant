import pytest

from app.ai.evaluation.evaluation_history import (
    compare_latest_runs,
)

from app.database.session import SessionLocal

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def test_compare_latest_runs_in_database():
    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        previous = repository.create_run(
            dataset_name="history-test-v1",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        )

        current = repository.create_run(
            dataset_name="history-test-v2",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=0.75,
            average_semantic_relevance=0.65,
            average_source_count=1.0,
            overall_pass_rate=0.50,
            quality_gate_passed=False,
        )

        comparison = compare_latest_runs(repository)

        assert comparison is not None

        assert comparison.groundedness_delta == pytest.approx(-0.25)

        assert comparison.semantic_relevance_delta == pytest.approx(0.05)
        assert comparison.overall_pass_rate_delta == pytest.approx(-0.50)

        db.delete(previous)
        db.delete(current)
        db.commit()

    finally:
        db.close()
