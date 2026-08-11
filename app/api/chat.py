from fastapi import APIRouter

from pydantic import BaseModel

from fastapi.responses import StreamingResponse

from fastapi import Depends

from app.auth.dependencies import get_current_user

from app.models.user import User

from functools import lru_cache

from app.repositories.dependencies import (
    get_chat_repository,
)

from app.repositories.chat_repository import (
    ChatRepository,
)

from app.schemas.chat import (
    ChatQuestion,
    ChatSessionCreate,
    ChatSessionRename,
)

from app.services.conversation_dependencies import (
    get_conversation_service,
)

from app.services.conversation_service import (
    ConversationService,
)

from app.ai.chat.chatbot_service import (
    ChatbotService,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str



@lru_cache
def get_chatbot_service():
    return ChatbotService()


@router.post(
    "/ask",
    response_model=ChatResponse,
)
def ask(
    request: ChatRequest,
    service: ChatbotService = Depends(get_chatbot_service),
):
    answer = service.ask(request.question)

    return ChatResponse(answer=answer)



from app.ai.streaming.dependencies import (
    get_streaming_service,
)

from app.ai.streaming.stream_service import (
    StreamingService,
)


@router.post("/stream")
async def stream_chat(
    question: str,
    streaming: StreamingService = Depends(get_streaming_service),
):

    generator = streaming.stream(question)

    return StreamingResponse(
        generator,
        media_type="event-stream",
    )


@router.post("/sessions")
def create_session(
    request: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    repository: ChatRepository = Depends(get_chat_repository),
):

    return repository.create_session(
        current_user.id,
        request.title,
    )


@router.get("/sessions")
def list_sessions(
    current_user: User = Depends(get_current_user),
    repository: ChatRepository = Depends(get_chat_repository),
):

    return repository.get_sessions(current_user.id)


@router.get("/sessions/{session_id}")
def get_session(
    session_id: int,
    repository: ChatRepository = Depends(get_chat_repository),
):

    return repository.get_session(session_id)


@router.put("/sessions/{session_id}")
def rename_session(
    session_id: int,
    request: ChatSessionRename,
    repository: ChatRepository = Depends(get_chat_repository),
):

    return repository.rename_session(
        session_id,
        request.title,
    )


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    repository: ChatRepository = Depends(get_chat_repository),
):

    repository.delete_session(session_id)

    return {"message": "Session deleted"}


@router.post("/sessions/{session_id}/messages")
async def chat(
    session_id: int,
    request: ChatQuestion,
    service: ConversationService = Depends(get_conversation_service),
):

    generator = service.ask(
        session_id,
        request.question,
    )

    return StreamingResponse(
        generator,
        media_type="text/plain",
    )
