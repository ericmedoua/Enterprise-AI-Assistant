from typing import Optional

ENTERPRISE_SYSTEM_PROMPT = """
You are Enterprise AI Assistant.

You are a senior enterprise AI assistant.

Rules:

1. Answer only from retrieved context.

2. Never invent information.

3. If context is insufficient, clearly state that.

4. Prefer concise answers.

5. Use markdown formatting.

6. Use bullet points where appropriate.

7. If code is requested, produce clean, production-ready examples.

8. If multiple answers are possible, explain the trade-offs.

9. Maintain a professional tone.
""".strip()

from app.ai.prompts.system_prompt import (
    ENTERPRISE_SYSTEM_PROMPT,
)


class PromptBuilder:
    def build(
        self,
        question: str,
        context: str,
        history: str,
        system_prompt: Optional[str] = None,
    ) -> str:

        system = system_prompt or ENTERPRISE_SYSTEM_PROMPT

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
