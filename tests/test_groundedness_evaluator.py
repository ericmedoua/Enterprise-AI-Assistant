from app.ai.evaluation.groundedness_evaluator import (
    groundedness_score,
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
