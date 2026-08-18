import re
from dataclasses import dataclass


@dataclass
class GroundednessResult:
    score: float
    supported_sentences: int
    total_sentences: int


def _normalize_text(text: str) -> str:
    """
    Normalize text for simple lexical comparison.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def evaluate_groundedness(
    answer: str,
    context: str,
) -> GroundednessResult:
    """
    Evaluate how much of the answer is directly supported
    by the retrieved context.
    """

    if not answer.strip() or not context.strip():
        return GroundednessResult(
            score=0.0,
            supported_sentences=0,
            total_sentences=0,
        )

    normalized_context = _normalize_text(context)

    sentences = [
        sentence.strip()
        for sentence in re.split(
            r"[.!?]+",
            answer,
        )
        if sentence.strip()
    ]

    if not sentences:
        return GroundednessResult(
            score=0.0,
            supported_sentences=0,
            total_sentences=0,
        )

    supported = 0

    for sentence in sentences:
        normalized_sentence = _normalize_text(sentence)

        if normalized_sentence in normalized_context:
            supported += 1

    total = len(sentences)

    return GroundednessResult(
        score=supported / total,
        supported_sentences=supported,
        total_sentences=total,
    )


def groundedness_score(
    answer: str,
    context: str,
) -> float:
    """
    Backwards-compatible convenience function.
    """

    return evaluate_groundedness(
        answer,
        context,
    ).score


def is_grounded(
    result: GroundednessResult,
    threshold: float = 1.0,
) -> bool:
    """
    Return True when the groundedness score meets
    or exceeds the configured threshold.
    """

    return result.score >= threshold
