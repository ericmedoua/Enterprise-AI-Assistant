from app.ai.evaluation.benchmark import (
    run_rag_benchmark,
)

from app.ai.evaluation.datasets.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)


def test_real_rag_benchmark():
    results = run_rag_benchmark(RAG_EVALUATION_DATASET)

    assert len(results) == (len(RAG_EVALUATION_DATASET))

    for case, result in zip(
        RAG_EVALUATION_DATASET,
        results,
    ):
        print(f"\nQUESTION: {case.question}")

        print(f"Retrieval hit: {result.retrieval_hit}")

        print(f"Groundedness: {result.groundedness.score:.4f}")

        print(f"Semantic relevance: {result.semantic_relevance.score:.4f}")

        print(f"Sources: {result.source_count}")

        print(f"Overall: {result.overall_pass}")
