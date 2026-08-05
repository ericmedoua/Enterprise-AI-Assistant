from app.ai.embeddings.embedding_service import (
    EmbeddingService,
)

from app.ai.vectorstore.chroma_service import (
    ChromaService,
)

embedding_service = EmbeddingService()
vector_db = ChromaService()

text = """
Python is a popular programming language used
for backend development, AI, and automation.
"""

embedding = embedding_service.embed(text)

vector_db.add_document(
    document_id="doc1",
    text=text,
    embedding=embedding,
)

print("Document stored successfully.")
