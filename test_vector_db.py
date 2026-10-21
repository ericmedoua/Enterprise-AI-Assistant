from app.ai.embeddings.dependencies import get_embedding_service
from app.ai.vectorstore.chroma_service import ChromaService


def main() -> None:
    embedding_service = get_embedding_service()
    vector_db = ChromaService()

    text = """
    Python is a popular programming language used
    for backend development, AI, and automation.
    """

    embedding = embedding_service.embed_query(text)

    vector_db.add_document(
        document_id="doc1",
        text=text,
        embedding=embedding,
    )

    print("Document stored successfully.")


if __name__ == "__main__":
    main()
