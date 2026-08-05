def format_sources(documents):

    seen = set()

    lines = []

    for document in documents:
        source = document.metadata.get(
            "source",
            "Unknown",
        )

        page = document.metadata.get(
            "page",
            "?",
        )

        key = (
            source,
            page,
        )

        if key in seen:
            continue

        seen.add(key)

        lines.append(f"- {source} (Page {page})")

    return "\n".join(lines)
