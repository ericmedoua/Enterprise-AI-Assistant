from langchain_core.documents import Document

from app.ai.evaluation.retrieval_evaluator import (
    retrieval_hit,
)


def test_retrieval_hit_when_expected_source_is_present():
    documents = [
        Document(
            page_content="Monkeys swing from trees.",
            metadata={
                "source": "This Book Belongs To.pdf",
                "page": 1,
            },
        ),
    ]

    assert (
        retrieval_hit(
            documents,
            "This Book Belongs To.pdf",
        )
        is True
    )


def test_retrieval_miss_when_expected_source_is_absent():
    documents = [
        Document(
            page_content="Reindeer have antlers.",
            metadata={
                "source": "Other.pdf",
                "page": 2,
            },
        ),
    ]

    assert (
        retrieval_hit(
            documents,
            "This Book Belongs To.pdf",
        )
        is False
    )


def test_retrieval_miss_when_no_documents_are_returned():
    assert (
        retrieval_hit(
            [],
            "This Book Belongs To.pdf",
        )
        is False
    )
