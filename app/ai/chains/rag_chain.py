# app/ai/chains/rag_chain.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.ai.prompts.chat_prompt import chat_prompt

from app.ai.retrieval.source_formatter import (
    format_sources,
)

from app.ai.retrieval.timed_retriever import (
    TimedRetriever,
)
from app.observability import metrics



# def format_documents(documents):
#    return "\n\n".join(document.page_content for document in documents)


def build_context(documents):

    return "\n\n".join(document.page_content for document in documents)


def build_sources(documents):

    sources = []

    for document in documents:
        metadata = document.metadata or {}

        sources.append(
            {
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page"),
                "score": metadata.get("score"),
            }
        )

    return sources


def build_rag_chain(retriever, llm, metrics=None):

    if metrics is not None:
        retriever = TimedRetriever(
            retriever,
            metrics,
        )
    parser = StrOutputParser()

    chain = (
        {
            "context": (
                RunnableLambda(lambda x: x["question"])
                | retriever
                | RunnableLambda(build_context)
            ),
            "question": RunnableLambda(lambda x: x["question"]),
            "history": RunnableLambda(lambda x: x.get("history", [])),
            "summary": lambda x: x.get("summary", ""),
        }
        | chat_prompt
        | llm
        | parser
    )

    return chain


def format_documents(documents):

    context = "\n\n".join(document.page_content for document in documents)

    sources = format_sources(documents)

    return f"""
{context}

Sources

{sources}
"""
