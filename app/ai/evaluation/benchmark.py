from dataclasses import dataclass

from app.ai.evaluation.retrieval_evaluator import (
    retrieval_hit,
)
from app.ai.retrieval.dependencies import (
    get_retriever,
)
from app.ai.evaluation.groundedness_evaluator import (
    evaluate_groundedness,
)

from app.ai.evaluation.semantic_relevance_evaluator import (
    evaluate_text_relevance,
)

from app.ai.evaluation.rag_evaluation import (
    evaluate_rag_response,
)
from app.ai.embeddings.dependencies import (
    get_embedding_service,
)
from app.ai.evaluation.evaluation_report import (
    build_evaluation_report,
)


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_source: str
    expected_answer: str


@dataclass
class BenchmarkCaseResult:
    question: str
    expected_source: str
    passed: bool


@dataclass
class BenchmarkResult:
    total_cases: int
    passed_cases: int
    pass_rate: float
    case_results: list[BenchmarkCaseResult]


def calculate_benchmark_result(
    case_results: list[BenchmarkCaseResult],
) -> BenchmarkResult:
    """
    Aggregate per-case benchmark results.
    """

    if not case_results:
        return BenchmarkResult(
            total_cases=0,
            passed_cases=0,
            pass_rate=0.0,
            case_results=[],
        )

    passed_cases = sum(result.passed for result in case_results)

    total_cases = len(case_results)

    return BenchmarkResult(
        total_cases=total_cases,
        passed_cases=passed_cases,
        pass_rate=passed_cases / total_cases,
        case_results=case_results,
    )


def run_retrieval_benchmark(
    cases: list[EvaluationCase],
) -> BenchmarkResult:
    """
    Run the evaluation dataset against the real
    application retriever.
    """

    if not cases:
        return calculate_benchmark_result([])

    retriever = get_retriever()

    case_results = []

    for case in cases:
        documents = retriever.invoke(case.question)

        hit = retrieval_hit(
            documents,
            case.expected_source,
        )

        case_results.append(
            BenchmarkCaseResult(
                question=case.question,
                expected_source=case.expected_source,
                passed=hit,
            )
        )

    return calculate_benchmark_result(case_results)


def run_rag_benchmark(
    cases: list[EvaluationCase],
) -> list:
    """
    Run the evaluation dataset through the real retriever
    and LLM, then evaluate each generated response.
    """

    if not cases:
        return []

    retriever = get_retriever()

    # Import here to avoid unnecessary LLM initialization
    # when the retrieval-only benchmark is used.
    from app.ai.llm.dependencies import get_llm_dependency
    from app.ai.chains.rag_chain import build_rag_chain

    llm = get_llm_dependency()

    rag_chain = build_rag_chain(
        retriever=retriever,
        llm=llm,
    )

    embedding_service = get_embedding_service()

    results = []

    for case in cases:
        documents = retriever.invoke(case.question)

        context = "\n\n".join(document.page_content for document in documents)

        retrieval_hit_result = retrieval_hit(
            documents,
            case.expected_source,
        )

        answer = rag_chain.invoke(
            {
                "question": case.question,
                "history": [],
                "summary": "",
            }
        )

        groundedness = evaluate_groundedness(
            answer,
            context,
        )

        semantic_relevance = evaluate_text_relevance(
            case.question,
            answer,
            embedding_service,
        )

        unique_sources = {
            (document.metadata or {}).get(
                "source",
                "Unknown",
            )
            for document in documents
        }

        evaluation = evaluate_rag_response(
            retrieval_hit=retrieval_hit_result,
            groundedness=groundedness,
            semantic_relevance=semantic_relevance,
            source_count=len(unique_sources),
        )

        results.append(evaluation)

    return results


def run_rag_evaluation_report(
    cases: list[EvaluationCase],
):
    """
    Run the complete RAG benchmark and aggregate
    the individual evaluation results.
    """

    results = run_rag_benchmark(cases)

    return build_evaluation_report(results)
