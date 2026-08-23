from app.ai.evaluation.evaluation_report import (
    EvaluationReport,
)

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)

from app.ai.evaluation.evaluation_snapshot_writer import (
    write_evaluation_snapshot,
)

from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def test_write_evaluation_snapshot(tmp_path):
    snapshot = EvaluationSnapshot(
        dataset_name="rag-evaluation-v1",
        report=EvaluationReport(
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.60,
            average_source_count=1.0,
            overall_pass_rate=1.0,
        ),
        quality_gate=QualityGateResult(
            passed=True,
            retrieval_passed=True,
            groundedness_passed=True,
            semantic_relevance_passed=True,
            overall_passed=True,
        ),
        comparison=None,
    )

    output = tmp_path / "evaluation_snapshot.json"

    result = write_evaluation_snapshot(
        snapshot,
        output,
    )

    assert result.exists()

    content = result.read_text(encoding="utf-8")

    assert "rag-evaluation-v1" in content
    assert '"passed": true' in content
