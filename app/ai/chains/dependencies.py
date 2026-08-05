from functools import lru_cache

from app.ai.chains.rag_chain import build_rag_chain
from app.ai.llm.groq_client import get_llm
from app.ai.vectorstore.dependencies import get_vectorstore


@lru_cache
def get_rag_chain():

    vectorstore = get_vectorstore()

    retriever = vectorstore.as_retriever()

    llm = get_llm()

    return build_rag_chain(
        retriever,
        llm,
    )
