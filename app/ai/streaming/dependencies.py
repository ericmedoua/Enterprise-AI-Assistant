from fastapi import Depends

from app.ai.llm.groq_client import get_llm

from app.ai.streaming.stream_service import StreamingService


def get_streaming_service(
    llm=Depends(get_llm),
):

    return StreamingService(llm)
