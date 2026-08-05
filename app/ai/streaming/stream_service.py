from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage


class StreamingService:
    def __init__(self, llm):

        self.llm = llm

    async def stream(
        self,
        prompt: str,
    ) -> AsyncGenerator[str, None]:

        async for chunk in self.llm.astream([HumanMessage(content=prompt)]):
            if chunk.content:
                yield chunk.content
