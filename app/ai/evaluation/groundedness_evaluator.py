import re


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


def groundedness_score(
    answer: str,
    context: str,
) -> float:
    """
    Estimate how much of the answer is directly supported
    by the retrieved context.

    Returns a value between 0.0 and 1.0.
    """

    if not answer.strip():
        return 0.0

    if not context.strip():
        return 0.0

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
        return 0.0

    supported = 0

    for sentence in sentences:
        normalized_sentence = _normalize_text(sentence)

        if normalized_sentence in normalized_context:
            supported += 1

    return supported / len(sentences)
