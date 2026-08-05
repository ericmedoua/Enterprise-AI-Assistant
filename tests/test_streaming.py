import asyncio

from app.ai.llm.groq_client import get_llm

from app.ai.streaming.stream_service import StreamingService


async def main():

    service = StreamingService(get_llm())

    async for token in service.stream("Explain what FastAPI is."):
        print(
            token,
            end="",
            flush=True,
        )


asyncio.run(main())
