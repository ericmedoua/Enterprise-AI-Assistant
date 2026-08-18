import re
from dataclasses import dataclass


@dataclass
class RelevanceResult:
    score: float
    matched_terms: int
    question_terms: int


def _normalize_text(text: str) -> list[str]:
    """
    Normalize text into simple word tokens.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    return [token for token in text.split() if token]


def _meaningful_terms(text: str) -> set[str]:
    """
    Return normalized terms while removing very common
    question/grammar words.
    """

    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "do",
        "does",
        "for",
        "how",
        "in",
        "is",
        "of",
        "on",
        "the",
        "to",
        "what",
        "where",
        "who",
        "why",
    }

    return {token for token in _normalize_text(text) if token not in stop_words}


def evaluate_relevance(
    question: str,
    answer: str,
) -> RelevanceResult:
    """
    Estimate answer relevance using lexical overlap
    between the question and answer.
    """

    question_terms = _meaningful_terms(question)

    if not question_terms:
        return RelevanceResult(
            score=0.0,
            matched_terms=0,
            question_terms=0,
        )

    answer_terms = _meaningful_terms(answer)

    matched_terms = len(question_terms.intersection(answer_terms))

    score = matched_terms / len(question_terms)

    return RelevanceResult(
        score=score,
        matched_terms=matched_terms,
        question_terms=len(question_terms),
    )


def relevance_score(
    question: str,
    answer: str,
) -> float:
    """
    Backwards-compatible convenience function.
    """

    return evaluate_relevance(
        question,
        answer,
    ).score


def is_relevant(
    result: RelevanceResult,
    threshold: float = 0.5,
) -> bool:
    """
    Return True when the relevance score meets
    or exceeds the threshold.
    """

    return result.score >= threshold
