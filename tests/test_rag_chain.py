from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage

from app.ai.chains.rag_chain import build_rag_chain
from app.ai.llm.dependencies import get_llm_dependency
from app.ai.retrieval.dependencies import get_retriever


retriever = get_retriever()

llm = get_llm_dependency()

chain = build_rag_chain(
    retriever=retriever,
    llm=llm,
)

answer = chain.invoke(
    {
        "question": "What is Python?",
        "history": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi!"),
        ],
        "summary": "",
    }
)

print(answer)
