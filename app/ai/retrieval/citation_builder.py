from app.schemas.citation import Citation


def build_citations(documents):

    citations = []

    seen = set()

    for document in documents:
        metadata = document.metadata

        key = (
            metadata.get("source"),
            metadata.get("page"),
        )

        if key in seen:
            continue

        seen.add(key)

        citations.append(
            Citation(
                source=metadata.get("source"),
                page=metadata.get("page"),
                chunk=metadata.get("chunk"),
            )
        )

    return citations
