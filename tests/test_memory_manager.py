from app.ai.memory.memory_manager import MemoryManager

from app.repositories.chat_repository import ChatRepository

from app.database.session import SessionLocal

db = SessionLocal()

repo = ChatRepository(db)

manager = MemoryManager(repo)

snapshot = manager.load(1)

print(snapshot.summary)

print(snapshot.recent_messages)
