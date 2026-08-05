import chromadb


class ChromaService:
    def __init__(self):

        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = self.client.get_or_create_collection(
            name="enterprise_documents"
        )

    def add_document(
        self,
        document_id: str,
        text: str,
        embedding: list[float],
    ):
        self.collection.add(
            ids=[document_id],
            documents=[text],
            embeddings=[embedding],
        )

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ):
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )
