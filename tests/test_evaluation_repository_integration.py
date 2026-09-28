import pytest

from sqlalchemy.exc import IntegrityError

from app.models.evaluation_run import EvaluationRun
from app.database.session import SessionLocal
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)
from app.repositories.evaluation_history_filters import (
    EvaluationHistoryFilters,
    EvaluationHistoryQuery,
)

pytestmark = pytest.mark.integration


def test_create_and_read_evaluation_run():
    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        created = repository.create_run(
            dataset_name="rag-evaluation-v1",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.5971,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        )

        assert created.id is not None
        assert created.dataset_name == ("rag-evaluation-v1")

        loaded = repository.get_run(created.id)

        assert loaded is not None
        assert loaded.id == created.id
        assert loaded.total_cases == 2
        assert loaded.retrieval_hit_rate == 1.0
        assert loaded.quality_gate_passed is True

        db.delete(created)
        db.commit()

    finally:
        db.close()


def test_list_evaluation_runs():
    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        first = repository.create_run(
            dataset_name="rag-evaluation-v1",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.59,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        )

        second = repository.create_run(
            dataset_name="rag-evaluation-v2",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=0.5,
            average_groundedness=0.8,
            average_semantic_relevance=0.42,
            average_source_count=1.0,
            overall_pass_rate=0.5,
            quality_gate_passed=False,
        )

        runs = repository.list_runs()

        ids = {run.id for run in runs}

        assert first.id in ids
        assert second.id in ids

        db.query(type(first))

        db.delete(first)
        db.delete(second)
        db.commit()

    finally:
        db.close()


def test_get_latest_run():
    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        first = repository.create_run(
            dataset_name="historical-v1",
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

        second = repository.create_run(
            dataset_name="historical-v2",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=0.75,
            average_semantic_relevance=0.61,
            average_source_count=1.0,
            overall_pass_rate=0.5,
            quality_gate_passed=False,
        )

        latest = repository.get_latest_run()

        assert latest is not None
        assert latest.id == second.id
        assert latest.dataset_name == "historical-v2"

        db.delete(first)
        db.delete(second)
        db.commit()

    finally:
        db.close()


def test_get_previous_run():
    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        first = repository.create_run(
            dataset_name="historical-v1",
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

        second = repository.create_run(
            dataset_name="historical-v2",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=0.75,
            average_semantic_relevance=0.61,
            average_source_count=1.0,
            overall_pass_rate=0.5,
            quality_gate_passed=False,
        )

        previous = repository.get_previous_run(current_run_id=second.id)

        assert previous is not None
        assert previous.id == first.id

        db.delete(first)
        db.delete(second)
        db.commit()

    finally:
        db.close()


def test_database_rejects_invalid_retrieval_hit_rate():
    db = SessionLocal()

    try:
        invalid_run = EvaluationRun(
            dataset_name="constraint-test",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.5,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
            status="completed",
        )

        db.add(invalid_run)

        with pytest.raises(IntegrityError):
            db.flush()

        db.rollback()

    finally:
        db.close()


def test_database_rejects_invalid_evaluation_status():
    db = SessionLocal()

    try:
        invalid_run = EvaluationRun(
            dataset_name="constraint-test",
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
            status="invalid-status",
        )

        db.add(invalid_run)

        with pytest.raises(IntegrityError):
            db.flush()

        db.rollback()

    finally:
        db.close()


def test_evaluation_history_query_filters_sorts_and_paginates():
    db = SessionLocal()

    try:
        repository = EvaluationRepository(db)

        first = repository.create_run(
            dataset_name="history-query-test",
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
            dataset_name="history-query-test",
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

        excluded_quality_gate = repository.create_run(
            dataset_name="history-query-test",
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

        excluded_dataset = repository.create_run(
            dataset_name="different-dataset",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="test-commit",
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=1.0,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        )

        history_filters = EvaluationHistoryFilters(
            dataset_name="history-query-test",
            quality_gate_passed=True,
        )

        history_query = EvaluationHistoryQuery(
            filters=history_filters,
            limit=1,
            offset=1,
            sort_by="overall_pass_rate",
            sort_order="desc",
        )

        total = repository.count_runs(
            query=history_query,
        )

        runs = repository.list_runs(
            query=history_query,
        )

        assert total == 2
        assert len(runs) == 1
        assert runs[0].id == second.id
        assert runs[0].id != first.id
        assert runs[0].id != excluded_quality_gate.id
        assert runs[0].id != excluded_dataset.id

        db.delete(first)
        db.delete(second)
        db.delete(excluded_quality_gate)
        db.delete(excluded_dataset)
        db.commit()

    finally:
        db.close()
