from langchain_core.documents import Document


def merge_results(
    semantic_docs: list[Document],
    keyword_docs: list[Document],
) -> list[Document]:

    merged = []

    seen = set()

    for document in semantic_docs + keyword_docs:
        key = (
            document.metadata.get("source"),
            document.metadata.get("page"),
            document.metadata.get("chunk"),
        )

        if key in seen:
            continue

        seen.add(key)

        merged.append(document)

    return merged
