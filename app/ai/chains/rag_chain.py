# app/ai/chains/rag_chain.py

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.ai.prompts.chat_prompt import chat_prompt
from app.ai.retrieval.source_formatter import format_sources
from app.ai.retrieval.timed_retriever import TimedRetriever


def build_context(documents):
    """
    Convert retrieved LangChain Documents into the context
    that will be provided to the LLM.
    """

    if not documents:
        return "No relevant documents were found."

    return "\n\n".join(document.page_content for document in documents)


def has_documents(documents):
    """
    Determine whether retrieval returned usable documents.
    """
    return bool(documents)


def retrieve_documents(question, retriever):
    """
    Execute the retriever and return LangChain Documents.
    """

    return retriever.invoke(question)


def build_rag_chain(retriever, llm, metrics=None):
    """
    Build the RAG pipeline.

    Flow:

        question
            ↓
        retriever
            ↓
        documents
            ↓
        context + sources
            ↓
        chat prompt
            ↓
        LLM
            ↓
        string response
    """

    # Wrap the retriever with timing/observability when metrics
    # are provided.
    if metrics is not None:
        retriever = TimedRetriever(
            retriever,
            metrics,
        )

    parser = StrOutputParser()

    def retrieve(question):
        return retrieve_documents(
            question,
            retriever,
        )

    chain = (
        {
            # Retrieve documents from the user's question.
            "documents": (
                RunnableLambda(lambda x: x["question"]) | RunnableLambda(retrieve)
            ),
            # Pass the original question forward.
            "question": RunnableLambda(lambda x: x["question"]),
            # Pass recent conversation history forward.
            "history": RunnableLambda(lambda x: x.get("history", [])),
            # Pass conversation summary forward.
            "summary": RunnableLambda(lambda x: x.get("summary", "")),
        }
        # Convert retrieved documents into the values
        # expected by chat_prompt.
        | RunnableLambda(
            lambda x: {
                "context": build_context(x["documents"]),
                "sources": format_sources(x["documents"]),
                "has_context": has_documents(x["documents"]),
                "question": x["question"],
                "history": x["history"],
                "summary": x["summary"],
            }
        )
        # Build the ChatPromptTemplate.
        | chat_prompt
        # Send the prompt to the LLM.
        | llm
        # Convert the LLM response into a string.
        | parser
    )

    return chain
