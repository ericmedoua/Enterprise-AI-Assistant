from app.ai.evaluation.benchmark import (
    BenchmarkCaseResult,
    EvaluationCase,
    calculate_benchmark_result,
)


def test_evaluation_case():
    case = EvaluationCase(
        question="What do monkeys do?",
        expected_source="This Book Belongs To.pdf",
        expected_answer=("Monkeys swing from trees and love bananas."),
    )

    assert case.question == "What do monkeys do?"
    assert case.expected_source == ("This Book Belongs To.pdf")


def test_benchmark_case_result():
    result = BenchmarkCaseResult(
        question="What do monkeys do?",
        expected_source="This Book Belongs To.pdf",
        passed=True,
    )

    assert result.passed is True
    assert result.question == "What do monkeys do?"


def test_benchmark_result():
    case_results = [
        BenchmarkCaseResult(
            question="Q1",
            expected_source="A.pdf",
            passed=True,
        ),
        BenchmarkCaseResult(
            question="Q2",
            expected_source="B.pdf",
            passed=True,
        ),
        BenchmarkCaseResult(
            question="Q3",
            expected_source="C.pdf",
            passed=False,
        ),
        BenchmarkCaseResult(
            question="Q4",
            expected_source="D.pdf",
            passed=True,
        ),
    ]

    result = calculate_benchmark_result(case_results)

    assert result.total_cases == 4
    assert result.passed_cases == 3
    assert result.pass_rate == 0.75
    assert len(result.case_results) == 4


def test_empty_benchmark():
    result = calculate_benchmark_result([])

    assert result.total_cases == 0
    assert result.passed_cases == 0
    assert result.pass_rate == 0.0
