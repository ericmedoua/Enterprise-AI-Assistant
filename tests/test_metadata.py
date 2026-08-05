from app.ai.retrieval.dependencies import get_retriever

retriever = get_retriever()

documents = retriever.invoke("What is Spring Boot?")

for document in documents:
    print(document.metadata)
