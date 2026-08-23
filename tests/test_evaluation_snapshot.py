from app.ai.evaluation.evaluation_comparator import (
    EvaluationComparison,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)

from app.ai.evaluation.evaluation_snapshot_report import (
    format_evaluation_snapshot,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def test_format_evaluation_snapshot():
    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.95,
        average_semantic_relevance=0.61,
        average_source_count=1.0,
        overall_pass_rate=0.50,
    )

    gate = QualityGateResult(
        passed=False,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=False,
    )

    comparison = EvaluationComparison(
        retrieval_hit_rate_delta=0.0,
        groundedness_delta=-0.05,
        semantic_relevance_delta=0.02,
        source_count_delta=0.0,
        overall_pass_rate_delta=-0.50,
    )

    snapshot = EvaluationSnapshot(
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=gate,
        comparison=comparison,
    )

    output = format_evaluation_snapshot(snapshot)

    assert "RAG EVALUATION SNAPSHOT" in output
    assert "Dataset: rag-evaluation-v1" in output
    assert "Retrieval hit rate: 100.00%" in output
    assert "Groundedness: 95.00%" in output
    assert "Quality gate: FAIL" in output
    assert "Groundedness: -5.00%" in output
    assert "Overall pass rate: -50.00%" in output


def test_snapshot_without_comparison():
    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    gate = QualityGateResult(
        passed=True,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=True,
    )

    snapshot = EvaluationSnapshot(
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=gate,
        comparison=None,
    )

    output = format_evaluation_snapshot(snapshot)

    assert "Quality gate: PASS" in output
    assert "Historical Delta" not in output


def test_snapshot_to_dict():
    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    gate = QualityGateResult(
        passed=True,
        retrieval_passed=True,
        groundedness_passed=True,
        semantic_relevance_passed=True,
        overall_passed=True,
    )

    snapshot = EvaluationSnapshot(
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=gate,
        comparison=None,
    )

    data = snapshot.to_dict()

    assert data["dataset_name"] == ("rag-evaluation-v1")

    assert data["report"]["total_cases"] == 2

    assert data["report"]["retrieval_hit_rate"] == 1.0

    assert data["quality_gate"]["passed"] is True

    assert data["comparison"] is None
