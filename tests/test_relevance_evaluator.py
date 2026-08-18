from app.ai.evaluation.relevance_evaluator import (
    evaluate_relevance,
    is_relevant,
    relevance_score,
)


def test_relevant_answer():
    result = evaluate_relevance(
        "What do monkeys do?",
        "Monkeys swing from trees and love bananas.",
    )

    assert result.score == 1.0
    assert result.matched_terms == 1
    assert result.question_terms == 1


def test_partially_relevant_answer():
    result = evaluate_relevance(
        "What do monkeys do?",
        "Monkeys are animals that live in groups.",
    )

    assert result.score == 1.0


def test_irrelevant_answer():
    result = evaluate_relevance(
        "What do monkeys do?",
        "Reindeer have antlers.",
    )

    assert result.score == 0.0


def test_empty_question():
    result = evaluate_relevance(
        "",
        "Monkeys swing from trees.",
    )

    assert result.score == 0.0
    assert result.question_terms == 0


def test_relevance_score_helper():
    assert (
        relevance_score(
            "What do monkeys do?",
            "Monkeys swing from trees.",
        )
        == 1.0
    )


def test_is_relevant_above_threshold():
    result = evaluate_relevance(
        "What do monkeys do?",
        "Monkeys swing from trees.",
    )

    assert (
        is_relevant(
            result,
            threshold=0.5,
        )
        is True
    )


def test_is_not_relevant_below_threshold():
    result = evaluate_relevance(
        "What do monkeys do?",
        "Reindeer have antlers.",
    )

    assert (
        is_relevant(
            result,
            threshold=0.5,
        )
        is False
    )
