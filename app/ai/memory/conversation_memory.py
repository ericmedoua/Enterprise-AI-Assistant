from app.core.constants import MessageRole
from app.repositories.chat_repository import ChatRepository


class ConversationMemory:
    def __init__(
        self,
        repository: ChatRepository,
    ):

        self.repository = repository

    def load_history(
        self,
        session_id: int,
        limit: int = 20,
    ) -> list[dict]:

        messages = self.repository.get_messages(session_id)

        if limit > 0:
            messages = messages[-limit:]

        history = []

        for message in messages:
            history.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        return history

    def format_history(
        self,
        session_id: int,
        limit: int = 20,
    ) -> str:
        history = self.load_history(
            session_id=session_id,
            limit=limit,
        )

        if not history:
            return ""

        conversation = []

        for message in history:
            role = message["role"]

            if role == MessageRole.USER.value:
                speaker = "User"

            elif role == MessageRole.ASSISTANT.value:
                speaker = "Assistant"

            else:
                speaker = "System"

            conversation.append(f"{speaker}: {message['content']}")

        return "\n".join(conversation)

    def clear(
        self,
        session_id: int,
    ):

        self.repository.delete_messages(session_id)


if __name__ == "__main__":
    pass
    