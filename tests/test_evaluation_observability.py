from app.ai.evaluation.evaluation_observability import (
    build_evaluation_event,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def test_build_evaluation_event():
    report = EvaluationReport(
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.75,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=0.50,
    )

    gate = QualityGateResult(
        passed=False,
        retrieval_passed=True,
        groundedness_passed=False,
        semantic_relevance_passed=True,
        overall_passed=False,
    )

    snapshot = EvaluationSnapshot(
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=gate,
        comparison=None,
    )

    event = build_evaluation_event(snapshot)

    assert event.event_name == ("rag_evaluation_completed")

    assert event.dataset_name == ("rag-evaluation-v1")

    assert event.total_cases == 2
    assert event.retrieval_hit_rate == 1.0
    assert event.average_groundedness == 0.75
    assert event.average_semantic_relevance == 0.60
    assert event.overall_pass_rate == 0.50
    assert event.quality_gate_passed is False
    assert event.has_historical_comparison is False


def test_evaluation_event_to_dict():
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

    event = build_evaluation_event(snapshot)

    data = event.to_dict()

    assert data["event"] == ("rag_evaluation_completed")

    assert data["dataset"] == ("rag-evaluation-v1")

    assert data["quality_gate_passed"] is True
