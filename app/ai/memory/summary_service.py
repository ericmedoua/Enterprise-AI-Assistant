from app.ai.llm.groq_client import get_llm
from app.ai.memory.summary_prompt import summary_prompt


class SummaryService:
    def __init__(self):

        self.llm = get_llm()

        self.chain = summary_prompt | self.llm

    def summarize(
        self,
        conversation: str,
    ) -> str:

        response = self.chain.invoke(
            {
                "conversation": conversation,
            }
        )

        return response.content.strip()
