from app.ai.evaluation.benchmark import (
    run_retrieval_benchmark,
)

from tests.data.rag_evaluation_dataset import (
    RAG_EVALUATION_DATASET,
)


def test_real_retrieval_benchmark():
    result = run_retrieval_benchmark(RAG_EVALUATION_DATASET)

    print(f"\nBenchmark cases: {result.total_cases}")

    print(f"Benchmark passed: {result.passed_cases}")

    print(f"Retrieval pass rate: {result.pass_rate:.2%}")

    for case_result in result.case_results:
        status = (
            "PASS"
            if case_result.passed
            else "FAIL"
        )

        print(
            f"{status}: "
            f"{case_result.question}"
        )

    assert result.total_cases == (len(RAG_EVALUATION_DATASET))

    assert 0.0 <= result.pass_rate <= 1.0
