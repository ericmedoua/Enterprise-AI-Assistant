from app.ai.chains.rag_chain import build_rag_chain
from app.ai.retrieval.dependencies import get_retriever
from app.ai.llm.dependencies import get_llm_dependency

retriever = get_retriever()
llm = get_llm_dependency()

chain = build_rag_chain(
    retriever=retriever,
    llm=llm,
)

answer = chain.invoke(
    {
        "question": "Who won the FIFA World Cup in 1982?",
        "history": [],
        "summary": "",
    }
)

print(answer)
