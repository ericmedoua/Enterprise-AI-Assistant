from app.ai.evaluation.groundedness_evaluator import (
    evaluate_groundedness,
    groundedness_score,
    is_grounded,
)


def test_fully_grounded_answer():
    answer = "Monkeys swing from trees and love bananas."

    context = "Monkeys swing from trees and love bananas."

    assert (
        groundedness_score(
            answer,
            context,
        )
        == 1.0
    )


def test_partially_grounded_answer():
    answer = (
        "Monkeys swing from trees. Monkeys communicate using complex social signals."
    )

    context = "Monkeys swing from trees."

    assert (
        groundedness_score(
            answer,
            context,
        )
        == 0.5
    )


def test_ungrounded_answer():
    answer = "Monkeys are excellent swimmers."

    context = "Monkeys swing from trees and love bananas."

    assert (
        groundedness_score(
            answer,
            context,
        )
        == 0.0
    )


def test_empty_context():
    assert (
        groundedness_score(
            "Monkeys swing from trees.",
            "",
        )
        == 0.0
    )


def test_empty_answer():
    assert (
        groundedness_score(
            "",
            "Monkeys swing from trees.",
        )
        == 0.0
    )


def test_groundedness_result_contains_sentence_counts():
    result = evaluate_groundedness(
        "Monkeys swing from trees. Monkeys live on Mars.",
        "Monkeys swing from trees.",
    )

    assert result.score == 0.5
    assert result.supported_sentences == 1
    assert result.total_sentences == 2


def test_is_grounded_when_score_meets_threshold():
    result = evaluate_groundedness(
        "Monkeys swing from trees.",
        "Monkeys swing from trees.",
    )

    assert (
        is_grounded(
            result,
            threshold=1.0,
        )
        is True
    )


def test_is_not_grounded_when_score_is_below_threshold():
    result = evaluate_groundedness(
        "Monkeys swing from trees. Monkeys live on Mars.",
        "Monkeys swing from trees.",
    )

    assert (
        is_grounded(
            result,
            threshold=1.0,
        )
        is False
    )
