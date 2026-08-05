from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_template(
    """
You are an enterprise AI assistant.

Answer ONLY using the supplied context.

If the answer cannot be found,
reply with:

"I don't know based on the available documents."

Context:

{context}

Question:

{question}

Answer:
"""
)
