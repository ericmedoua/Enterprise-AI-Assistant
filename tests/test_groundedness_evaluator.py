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


def test_supported_paraphrased_sentence():
    result = evaluate_groundedness(
        "Monkeys love bananas.",
        "Monkeys swing from trees and love bananas.",
    )

    assert result.score == 1.0


def test_source_section_is_ignored():
    result = evaluate_groundedness(
        "Monkeys swing from trees.\n\nSource: This Book Belongs To.pdf (Page 29)",
        "Monkeys swing from trees and love bananas.",
    )

    assert result.score == 1.0


def test_bullet_point_answer_is_evaluated_correctly():
    result = evaluate_groundedness(
        "- Monkeys swing from trees.\n"
        "- Monkeys love bananas.\n\n"
        "Source: This Book Belongs To.pdf (Page 29)",
        "Monkeys swing from trees and love bananas.",
    )

    assert result.score == 1.0
    assert result.supported_sentences == 2
    assert result.total_sentences == 2


def test_reindeer_paraphrase_is_supported():
    result = evaluate_groundedness(
        "- Reindeer have antlers.\n"
        "- In stories, reindeer are described as pulling sleds.",
        "Reindeer have antlers and pull sleds in stories.",
    )

    assert result.score == 1.0
