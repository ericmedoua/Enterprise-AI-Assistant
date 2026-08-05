from app.ai.chains.rag_chain import build_rag_chain

# from app.ai.retrieval.dependencies import get_retriever
from app.ai.llm.groq_client import get_llm
from app.ai.retrieval.dependencies import get_retriever


class ChatbotService:
    def __init__(
        self,
        retriever=None,
        llm=None,
        chain=None,
    ):

        self.llm = llm or get_llm()

        self.retriever = retriever or get_retriever()

        self.chain = chain or build_rag_chain(
            self.retriever,
            self.llm,
        )

    def ask(
        self,
        question: str,
        history: list | str = "",
    ):

        return self.chain.invoke(
            {
                "question": question,
                "history": history,
            }
        )
