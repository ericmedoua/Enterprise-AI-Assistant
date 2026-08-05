from app.ai.vectorstore.chroma_service import ChromaService
from app.ai.retrieval.result_formatter import build_retrieval_results

vectorstore = ChromaService()

results = vectorstore.similarity_search_with_score(
    "What is APEX?",
    k=3,
)

formatted = build_retrieval_results(results)

for item in formatted:
    print(item)
