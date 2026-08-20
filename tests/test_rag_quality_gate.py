from app.ai.evaluation.benchmark import (
    run_rag_evaluation_report,
)

from app.ai.evaluation.quality_gate import (
    evaluate_quality_gate,
)

from tests.data.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)


def test_real_rag_quality_gate():
    report = run_rag_evaluation_report(RAG_EVALUATION_DATASET)

    result = evaluate_quality_gate(report)

    print("\n")
    print(f"Retrieval hit rate: {report.retrieval_hit_rate:.2%}")

    print(f"Groundedness: {report.average_groundedness:.2%}")

    print(f"Semantic relevance: {report.average_semantic_relevance:.2%}")

    print(f"Overall pass rate: {report.overall_pass_rate:.2%}")

    print(f"Quality gate: {'PASS' if result.passed else 'FAIL'}")

    assert result.passed is True
