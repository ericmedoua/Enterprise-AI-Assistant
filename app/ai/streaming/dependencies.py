from fastapi import Depends

from app.ai.llm.dependencies import get_llm_dependency
from app.ai.retrieval.dependencies import get_user_retriever
from app.ai.streaming.stream_service import StreamingService


def get_streaming_service(
    llm=Depends(get_llm_dependency),
    retriever=Depends(get_user_retriever),
):
    """Build a request-scoped streaming RAG service.

    FastAPI resolves ``get_user_retriever`` from the authenticated request,
    ensuring streamed answers use the same document-ownership filter as
    non-streaming chat.
    """
    return StreamingService(llm=llm, retriever=retriever)
