from fastapi import Depends

from app.ai.llm.dependencies import get_llm_dependency
from app.ai.retrieval.dependencies import get_retriever
from app.repositories.dependencies import get_chat_repository
from .conversation_service import ConversationService
from app.observability.dependencies import get_observability


def get_conversation_service(
    repository=Depends(get_chat_repository),
    retriever=Depends(get_retriever),
    llm=Depends(get_llm_dependency),
    observability=Depends(get_observability),
):

    return ConversationService(
        repository=repository,
        retriever=retriever,
        llm=llm,
        observability=observability,
    )
