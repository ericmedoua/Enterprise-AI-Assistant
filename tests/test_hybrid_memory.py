from app.database.session import SessionLocal

from app.repositories.chat_repository import ChatRepository

from app.ai.memory.memory_manager import MemoryManager

db = SessionLocal()

repo = ChatRepository(db)

manager = MemoryManager(repo)

snapshot = manager.load(1)

print("SUMMARY")
print("-" * 40)
print(snapshot.summary)

print()

print("RECENT")
print("-" * 40)

for message in snapshot.recent_messages:
    print(message.type)
    print(message.content)
    print()
