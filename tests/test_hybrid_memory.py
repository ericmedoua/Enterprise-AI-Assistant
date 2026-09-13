from app.ai.memory.memory_manager import MemoryManager
from app.repositories.chat_repository import ChatRepository


def test_hybrid_memory(db, test_session):
    repository = ChatRepository(db)

    repository.save_message(
        test_session.id,
        "user",
        "What is FastAPI?",
    )

    repository.save_message(
        test_session.id,
        "assistant",
        "FastAPI is a Python web framework.",
    )

    manager = MemoryManager(repository)

    snapshot = manager.load(test_session.id)

    assert snapshot is not None
    assert snapshot.summary == ""
    assert len(snapshot.recent_messages) == 2
