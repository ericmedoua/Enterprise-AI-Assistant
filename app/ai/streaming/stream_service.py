from collections.abc import AsyncGenerator

from app.ai.chains.rag_chain import build_rag_chain


class StreamingService:
    """Stream RAG answers using a caller-scoped retriever.

    The retriever must be created by the authenticated request dependency. Do
    not create an unscoped vector-store retriever inside this service.
    """

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.chain = build_rag_chain(retriever=retriever, llm=llm)

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async for chunk in self.chain.astream(
            {"question": prompt, "history": [], "summary": ""}
        ):
            if chunk:
                yield chunk
