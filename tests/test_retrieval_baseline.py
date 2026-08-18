from app.ai.evaluation.retrieval_evaluator import (
    retrieval_hit,
    retrieval_hit_rate,
)
from app.ai.retrieval.dependencies import get_retriever

from tests.data.retrieval_baseline import (
    BASELINE_RETRIEVAL_HIT_RATE,
)
from tests.data.retrieval_questions import (
    RETRIEVAL_EVALUATION_CASES,
)


def test_real_retriever_baseline():
    retriever = get_retriever()

    results = []

    for case in RETRIEVAL_EVALUATION_CASES:
        documents = retriever.invoke(case["question"])

        hit = retrieval_hit(
            documents,
            case["expected_source"],
        )

        results.append(hit)

    hit_rate = retrieval_hit_rate(results)

    print(f"\nRetrieval baseline hit rate: {hit_rate:.2%}")

    assert hit_rate >= BASELINE_RETRIEVAL_HIT_RATE
