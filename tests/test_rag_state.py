from langchain_core.documents import Document

from app.ai.chains.rag_chain import (
    build_context,
    has_documents,
)


def test_has_documents_returns_true_for_retrieved_documents():
    documents = [
        Document(
            page_content="Monkeys swing from trees.",
            metadata={
                "source": "This Book Belongs To.pdf",
                "page": 1,
            },
        )
    ]

    assert has_documents(documents) is True


def test_has_documents_returns_false_when_no_documents_are_retrieved():
    assert has_documents([]) is False


def test_build_context_handles_empty_documents():
    assert build_context([]) == "No relevant documents were found."


def test_build_context_contains_document_content():
    documents = [
        Document(
            page_content="Monkeys swing from trees.",
            metadata={
                "source": "This Book Belongs To.pdf",
                "page": 1,
            },
        ),
        Document(
            page_content="Monkeys love bananas.",
            metadata={
                "source": "This Book Belongs To.pdf",
                "page": 2,
            },
        ),
    ]

    context = build_context(documents)

    assert "Monkeys swing from trees." in context
    assert "Monkeys love bananas." in context
