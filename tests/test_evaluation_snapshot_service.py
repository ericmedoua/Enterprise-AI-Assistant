import pytest

from unittest.mock import Mock

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.evaluation_snapshot_service import (
    build_evaluation_snapshot,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def test_build_evaluation_snapshot():
    repository = Mock()
    repository.get_latest_run.return_value = None

    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
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

    snapshot = build_evaluation_snapshot(
        repository=repository,
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=quality_gate,
    )

    assert snapshot.dataset_name == ("rag-evaluation-v1")

    assert snapshot.report is report
    assert snapshot.quality_gate is quality_gate
    assert snapshot.comparison is None


def test_build_evaluation_snapshot_with_history():
    repository = Mock()

    previous = Mock(
        id=1,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    current = Mock(
        id=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.90,
        average_semantic_relevance=0.65,
        average_source_count=1.0,
        overall_pass_rate=0.50,
    )

    repository.get_latest_run.return_value = current
    repository.get_previous_run.return_value = previous
    repository.get_run.return_value = current

    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.90,
        average_semantic_relevance=0.65,
        average_source_count=1.0,
        overall_pass_rate=0.50,
    )

    quality_gate = QualityGateResult(
        passed=False,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=False,
    )

    snapshot = build_evaluation_snapshot(
        repository=repository,
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=quality_gate,
        current_run_id=2,
    )

    assert snapshot.comparison is not None
    assert snapshot.comparison.groundedness_delta == pytest.approx(-0.10)

    assert snapshot.comparison.semantic_relevance_delta == pytest.approx(0.05)
