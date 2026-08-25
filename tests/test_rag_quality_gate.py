import json

from app.ai.evaluation.benchmark import (
    run_rag_evaluation_report,
)

from app.ai.evaluation.quality_gate import (
    evaluate_quality_gate,
)

from app.ai.evaluation.evaluation_persistence import (
    persist_evaluation,
)

from app.database.session import (
    SessionLocal,
)

from app.ai.evaluation.datasets.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)

from app.ai.evaluation.evaluation_metadata import (
    get_evaluation_metadata,
)
from app.ai.evaluation.evaluation_snapshot_service import (
    build_evaluation_snapshot,
)

from app.ai.evaluation.evaluation_snapshot_report import (
    format_evaluation_snapshot,
)
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)
from app.ai.evaluation.evaluation_snapshot_writer import (
    write_evaluation_snapshot,
)
from app.ai.evaluation.evaluation_observability import (
    build_evaluation_event,
)

from app.ai.evaluation.evaluation_observability_logger import (
    log_evaluation_event,
)


def test_real_rag_quality_gate():
    report = run_rag_evaluation_report(RAG_EVALUATION_DATASET)

    result = evaluate_quality_gate(report)

    assert report.total_cases == len(RAG_EVALUATION_DATASET)

    assert 0.0 <= report.retrieval_hit_rate <= 1.0
    assert 0.0 <= report.average_groundedness <= 1.0
    assert 0.0 <= report.average_semantic_relevance <= 1.0
    assert report.average_source_count >= 0.0
    assert 0.0 <= report.overall_pass_rate <= 1.0

    assert result.retrieval_passed == (report.retrieval_hit_rate >= 1.0)

    assert result.groundedness_passed == (report.average_groundedness >= 0.90)

    assert result.semantic_relevance_passed == (
        report.average_semantic_relevance >= 0.50
    )

    assert result.overall_passed == (report.overall_pass_rate >= 1.0)

    db = SessionLocal()

    metadata = get_evaluation_metadata()

    try:
        evaluation_run = persist_evaluation(
            db=db,
            dataset_name="rag-evaluation-v1",
            llm_model=metadata.llm_model,
            embedding_model=metadata.embedding_model,
            git_commit=metadata.git_commit,
            report=report,
            quality_gate=result,
        )

        repository = EvaluationRepository(db)

        snapshot = build_evaluation_snapshot(
            repository=repository,
            dataset_name="rag-evaluation-v1",
            report=report,
            quality_gate=result,
            current_run_id=evaluation_run.id,
        )

        snapshot_path = write_evaluation_snapshot(
            snapshot,
            "artifacts/evaluation_snapshot.json",
        )

        event = build_evaluation_event(snapshot)

        log_evaluation_event(event)

        print("\n" + format_evaluation_snapshot(snapshot))
        print("\nEVALUATION_SNAPSHOT_JSON")
        print(
            json.dumps(
                snapshot.to_dict(),
                indent=2,
            )
        )
        print(f"\nEvaluation snapshot: {snapshot_path}")

        assert snapshot.dataset_name == "rag-evaluation-v1"
        assert snapshot.report is report
        assert snapshot.quality_gate is result
        previous_run = repository.get_previous_run(evaluation_run.id)

        if previous_run is not None:
            assert snapshot.comparison is not None
        else:
            assert snapshot.comparison is None

        assert evaluation_run.id is not None

        assert evaluation_run.dataset_name == "rag-evaluation-v1"

        assert evaluation_run.total_cases == report.total_cases

        assert evaluation_run.retrieval_hit_rate == report.retrieval_hit_rate

        assert evaluation_run.average_groundedness == report.average_groundedness

        assert (
            evaluation_run.average_semantic_relevance
            == report.average_semantic_relevance
        )

        assert evaluation_run.overall_pass_rate == report.overall_pass_rate

        assert evaluation_run.quality_gate_passed == result.passed

        print(f"\nPersisted evaluation run: {evaluation_run.id}")

        print(f"Quality gate: {'PASS' if result.passed else 'FAIL'}")

    finally:
        db.close()
