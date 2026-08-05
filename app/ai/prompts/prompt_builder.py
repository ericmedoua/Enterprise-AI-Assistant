from typing import Optional


DEFAULT_SYSTEM_PROMPT = """
You are Enterprise AI Assistant.

You are a professional AI assistant.

Answer ONLY using the provided context.

If the answer cannot be found,
say you don't know.

Never hallucinate.

Be concise.

Use markdown formatting.

""".strip()


class PromptBuilder:
    def build(
        self,
        question: str,
        context: str,
        history: str,
        system_prompt: Optional[str] = None,
    ) -> str:

        system = system_prompt or DEFAULT_SYSTEM_PROMPT

        return f"""
==============================
SYSTEM
==============================

{system}

==============================
CONVERSATION
==============================

{history}

==============================
DOCUMENT CONTEXT
==============================

{context}

==============================
USER QUESTION
==============================

{question}

==============================
ASSISTANT
==============================
""".strip()
