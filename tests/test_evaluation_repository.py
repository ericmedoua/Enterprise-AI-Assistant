from unittest.mock import Mock

from app.repositories.evaluation_repository import (
    EvaluationRepository,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def test_create_run():
    db = Mock()

    repository = EvaluationRepository(db)

    result = repository.create_run(
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

    assert result.dataset_name == ("rag-evaluation-v1")

    assert result.total_cases == 2
    assert result.retrieval_hit_rate == 1.0
    assert result.quality_gate_passed is True

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_from_evaluation():
    db = Mock()

    repository = EvaluationRepository(db)

    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.5971,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    quality_gate = QualityGateResult(
        passed=True,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=True,
    )

    result = repository.create_from_evaluation(
        dataset_name="rag-evaluation-v1",
        llm_model="openai/gpt-oss-120b",
        embedding_model="all-MiniLM-L6-v2",
        git_commit="test-commit",
        report=report,
        quality_gate=quality_gate,
    )

    assert result.dataset_name == ("rag-evaluation-v1")

    assert result.llm_model == "openai/gpt-oss-120b"
    assert result.embedding_model == "all-MiniLM-L6-v2"
    assert result.git_commit == "test-commit"

    assert result.total_cases == 2
    assert result.retrieval_hit_rate == 1.0
    assert result.average_groundedness == 1.0
    assert result.average_semantic_relevance == 0.5971
    assert result.average_source_count == 1.0
    assert result.overall_pass_rate == 1.0
    assert result.quality_gate_passed is True


def test_get_latest_run():
    db = Mock()

    repository = EvaluationRepository(db)

    latest = Mock()

    db.query.return_value.order_by.return_value.first.return_value = latest

    result = repository.get_latest_run()

    assert result is latest


def test_get_previous_run():
    db = Mock()

    repository = EvaluationRepository(db)

    previous = Mock()

    (
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value
    ) = previous

    result = repository.get_previous_run(current_run_id=10)

    assert result is previous

    db.query.return_value.filter.assert_called_once()
