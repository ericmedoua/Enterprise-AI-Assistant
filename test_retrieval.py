from app.ai.retrieval.retriever import Retriever

retriever = Retriever()

results = retriever.retrieve("What language is used for AI?")

print(results)
