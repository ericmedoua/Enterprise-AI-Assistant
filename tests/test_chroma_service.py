from app.ai.vectorstore.chroma_service import ChromaService

db = ChromaService()

print(type(db.vectorstore))
