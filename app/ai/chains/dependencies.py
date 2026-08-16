from functools import lru_cache

from app.ai.chains.rag_chain import build_rag_chain
from app.ai.llm.groq_client import get_llm
from app.ai.retrieval.dependencies import get_retriever


@lru_cache
def get_rag_chain():

    retriever = get_retriever()

    llm = get_llm()

    return build_rag_chain(
        retriever=retriever,
        llm=llm,
    )
