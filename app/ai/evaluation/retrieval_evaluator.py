from dataclasses import dataclass

from langchain_core.documents import Document


@dataclass
class RetrievalEvaluationResult:
    question: str
    expected_source: str
    hit: bool


def retrieval_hit(
    documents: list[Document],
    expected_source: str,
) -> bool:
    """
    Return True when at least one retrieved document
    comes from the expected source.
    """

    if not documents:
        return False

    for document in documents:
        metadata = document.metadata or {}

        source = metadata.get("source")

        if source == expected_source:
            return True

    return False


def retrieval_hit_rate(results: list[bool]) -> float:
    """
    Calculate retrieval hit rate as a value between 0 and 1.
    """

    if not results:
        return 0.0

    return sum(results) / len(results)
