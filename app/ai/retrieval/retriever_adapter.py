from app.ai.retrieval.retriever import Retriever


class LangChainRetriever:
    def __init__(self):
        self.retriever = Retriever()

    def retrieve(self, question: str):

        results = self.retriever.retrieve(question)

        documents = []

        for doc in results["documents"][0]:
            documents.append(doc)

        return documents
