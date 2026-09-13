from app.ai.memory.conversation_memory import ConversationMemory
from app.core.constants import MessageRole
from app.repositories.chat_repository import ChatRepository


def test_conversation_memory(db, test_session):
    repository = ChatRepository(db)

    repository.save_message(
        test_session.id,
        MessageRole.USER.value,
        "Hello",
    )

    repository.save_message(
        test_session.id,
        MessageRole.ASSISTANT.value,
        "Hi!",
    )

    repository.save_message(
        test_session.id,
        MessageRole.USER.value,
        "Tell me about Python.",
    )

    repository.save_message(
        test_session.id,
        MessageRole.ASSISTANT.value,
        "Python is a programming language.",
    )

    memory = ConversationMemory(repository)

    history = memory.format_history(test_session.id)

    assert history
    assert "Hello" in history
    assert "Tell me about Python." in history
    assert "Python is a programming language." in history
