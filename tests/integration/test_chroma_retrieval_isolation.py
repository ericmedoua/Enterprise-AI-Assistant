"""Integration tests for Chroma's per-user metadata filtering."""

from uuid import uuid4

import pytest
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma


class DeterministicEmbeddings(Embeddings):
    """Local fake embeddings; no external API is required."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        # A fixed, valid vector is sufficient because this test checks
        # metadata isolation, not semantic ranking.
        return [1.0, 0.0, 0.0]


@pytest.mark.integration
def test_chroma_retriever_isolates_users_and_excludes_legacy_chunks():
    collection_name = f"isolation_test_{uuid4().hex[:20]}"
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=DeterministicEmbeddings(),
    )

    try:
        vectorstore.add_texts(
            texts=[
                "Private handbook belonging to User A.",
                "Confidential notes belonging to User B.",
                "Legacy document with no ownership metadata.",
            ],
            metadatas=[
                {
                    "owner_id": "user-a",
                    "document_id": "doc-a",
                    "source": "a.txt",
                },
                {
                    "owner_id": "user-b",
                    "document_id": "doc-b",
                    "source": "b.txt",
                },
                {
                    "source": "legacy.txt",
                },
            ],
            ids=["doc-a-chunk-1", "doc-b-chunk-1", "legacy-chunk-1"],
        )

        retriever_a = vectorstore.as_retriever(
            search_kwargs={
                "k": 10,
                "filter": {"owner_id": "user-a"},
            }
        )
        retriever_b = vectorstore.as_retriever(
            search_kwargs={
                "k": 10,
                "filter": {"owner_id": "user-b"},
            }
        )

        results_a = retriever_a.invoke("handbook notes")
        results_b = retriever_b.invoke("handbook notes")

        contents_a = {doc.page_content for doc in results_a}
        contents_b = {doc.page_content for doc in results_b}

        assert contents_a == {"Private handbook belonging to User A."}
        assert contents_b == {"Confidential notes belonging to User B."}

        # Neither user should receive the other user's document.
        assert not contents_a.intersection(contents_b)

        # Documents without owner_id must not leak into either result.
        assert all("owner_id" in doc.metadata for doc in results_a)
        assert all("owner_id" in doc.metadata for doc in results_b)
        assert "Legacy document with no ownership metadata." not in contents_a
        assert "Legacy document with no ownership metadata." not in contents_b

    finally:
        vectorstore.delete_collection()


@pytest.mark.integration
def test_chroma_deletion_is_scoped_to_owner_and_document():
    from app.ai.vectorstore.chroma_service import ChromaService

    collection_name = f"delete_isolation_{uuid4().hex[:20]}"
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=DeterministicEmbeddings(),
    )

    service = ChromaService.__new__(ChromaService)
    service.vectorstore = vectorstore

    try:
        vectorstore.add_texts(
            texts=[
                "User A document A content.",
                "User A document B content.",
                "User B document A content.",
            ],
            metadatas=[
                {"owner_id": "user-a", "document_id": "doc-a"},
                {"owner_id": "user-a", "document_id": "doc-b"},
                {"owner_id": "user-b", "document_id": "doc-a"},
            ],
            ids=[
                "user-a-doc-a-chunk-1",
                "user-a-doc-b-chunk-1",
                "user-b-doc-a-chunk-1",
            ],
        )

        service.delete_document(
            owner_id="user-a",
            document_id="doc-a",
        )

        remaining = vectorstore.get(include=["metadatas", "documents"])

        remaining_ids = set(remaining["ids"])
        assert remaining_ids == {
            "user-a-doc-b-chunk-1",
            "user-b-doc-a-chunk-1",
        }

        remaining_metadata = {
            chunk_id: metadata
            for chunk_id, metadata in zip(
                remaining["ids"],
                remaining["metadatas"],
            )
        }

        assert remaining_metadata["user-a-doc-b-chunk-1"] == {
            "owner_id": "user-a",
            "document_id": "doc-b",
        }
        assert remaining_metadata["user-b-doc-a-chunk-1"] == {
            "owner_id": "user-b",
            "document_id": "doc-a",
        }

        retriever_a = vectorstore.as_retriever(
            search_kwargs={
                "k": 10,
                "filter": {"owner_id": "user-a"},
            }
        )
        retriever_b = vectorstore.as_retriever(
            search_kwargs={
                "k": 10,
                "filter": {"owner_id": "user-b"},
            }
        )

        results_a = retriever_a.invoke("document content")
        results_b = retriever_b.invoke("document content")

        assert {doc.page_content for doc in results_a} == {"User A document B content."}
        assert {doc.page_content for doc in results_b} == {"User B document A content."}

    finally:
        vectorstore.delete_collection()
