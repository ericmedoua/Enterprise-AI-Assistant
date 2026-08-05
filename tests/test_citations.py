from langchain_core.documents import Document

from app.ai.retrieval.citation_builder import build_citations


docs = [
    Document(
        page_content="A",
        metadata={
            "source": "sample.pdf",
            "page": 1,
            "chunk": 1,
        },
    ),
    Document(
        page_content="B",
        metadata={
            "source": "sample.pdf",
            "page": 1,
            "chunk": 2,
        },
    ),
    Document(
        page_content="C",
        metadata={
            "source": "sample.pdf",
            "page": 2,
            "chunk": 1,
        },
    ),
]

citations = build_citations(docs)

for citation in citations:
    print(citation)
