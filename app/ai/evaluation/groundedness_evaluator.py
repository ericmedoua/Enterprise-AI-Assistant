import re
from dataclasses import dataclass


@dataclass
class GroundednessResult:
    score: float
    supported_sentences: int
    total_sentences: int


def _normalize_text(text: str) -> str:
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


def _content_tokens(text: str) -> set[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "be",
        "been",
        "by",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "of",
        "on",
        "that",
        "the",
        "their",
        "they",
        "this",
        "to",
        "was",
        "were",
        "with",
    }

    normalized = _normalize_text(text)

    return {token for token in normalized.split() if token not in stop_words}


def _extract_answer_sentences(answer: str) -> list[str]:
    """
    Remove the generated citation section and extract
    the actual answer statements.
    """

    answer = re.split(
        r"\bsources?\s*:",
        answer,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    sentences = []

    for line in answer.splitlines():
        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"^[-*•]\s*",
            "",
            line,
        )

        parts = re.split(
            r"[.!?]+",
            line,
        )

        for part in parts:
            part = part.strip()

            if part:
                sentences.append(part)

    return sentences


def _sentence_support_score(
    sentence: str,
    context: str,
) -> float:
    sentence_tokens = _content_tokens(sentence)
    context_tokens = _content_tokens(context)

    if not sentence_tokens:
        return 0.0

    matched = sentence_tokens.intersection(context_tokens)

    return len(matched) / len(sentence_tokens)


def evaluate_groundedness(
    answer: str,
    context: str,
    support_threshold: float = 0.5,
) -> GroundednessResult:
    """
    Evaluate how much of the answer is supported
    by the retrieved context.

    A sentence is considered supported when at least
    support_threshold of its content words occur in
    the retrieved context.
    """

    if not answer.strip() or not context.strip():
        return GroundednessResult(
            score=0.0,
            supported_sentences=0,
            total_sentences=0,
        )

    sentences = _extract_answer_sentences(answer)

    if not sentences:
        return GroundednessResult(
            score=0.0,
            supported_sentences=0,
            total_sentences=0,
        )

    supported = 0

    for sentence in sentences:
        support_score = _sentence_support_score(
            sentence,
            context,
        )

        if support_score >= support_threshold:
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
    return evaluate_groundedness(
        answer,
        context,
    ).score


def is_grounded(
    result: GroundednessResult,
    threshold: float = 1.0,
) -> bool:
    return result.score >= threshold
