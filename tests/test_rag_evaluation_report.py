from app.ai.evaluation.benchmark import (
    run_rag_evaluation_report,
)

from tests.data.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)


def test_real_rag_evaluation_report():
    report = run_rag_evaluation_report(RAG_EVALUATION_DATASET)

    print(f"\nTotal cases: {report.total_cases}")

    print(f"Retrieval hit rate: {report.retrieval_hit_rate:.2%}")

    print(f"Average groundedness: {report.average_groundedness:.2%}")

    print(f"Average semantic relevance: {report.average_semantic_relevance:.2%}")

    print(f"Average source count: {report.average_source_count:.2f}")

    print(f"Overall pass rate: {report.overall_pass_rate:.2%}")

    assert report.total_cases == len(RAG_EVALUATION_DATASET)

    assert 0.0 <= report.retrieval_hit_rate <= 1.0
    assert 0.0 <= report.average_groundedness <= 1.0
    assert 0.0 <= report.average_semantic_relevance <= 1.0
    assert report.average_source_count >= 0.0
    assert 0.0 <= report.overall_pass_rate <= 1.0
