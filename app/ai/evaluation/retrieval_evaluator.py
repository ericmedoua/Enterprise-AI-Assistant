from langchain_core.documents import Document


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
