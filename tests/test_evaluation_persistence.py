from unittest.mock import Mock

from app.ai.evaluation.evaluation_persistence import (
    persist_evaluation,
)

from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def test_persist_evaluation():
    db = Mock()

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

    result = persist_evaluation(
        db=db,
        dataset_name="rag-evaluation-v1",
        report=report,
        quality_gate=quality_gate,
    )

    assert result.dataset_name == ("rag-evaluation-v1")

    assert result.total_cases == 2
    assert result.quality_gate_passed is True
    assert db.add.called
    assert db.commit.called
