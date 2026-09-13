from app.ai.memory.memory_manager import MemoryManager
from app.repositories.chat_repository import ChatRepository


def test_memory_manager(db, test_session):
    repository = ChatRepository(db)

    repository.save_message(
        test_session.id,
        "user",
        "Hello",
    )

    repository.save_message(
        test_session.id,
        "assistant",
        "Hi!",
    )

    manager = MemoryManager(repository)

    snapshot = manager.load(test_session.id)

    assert snapshot is not None
    assert snapshot.summary == ""
    assert len(snapshot.recent_messages) == 2
