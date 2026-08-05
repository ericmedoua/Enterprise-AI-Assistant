from app.ai.memory.conversation_memory import ConversationMemory
from app.database.session import SessionLocal
from app.repositories.chat_repository import ChatRepository
from app.core.constants import MessageRole

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

sys.path.insert(0, PROJECT_ROOT)

from app.ai.memory.conversation_memory import ConversationMemory


db = SessionLocal()

repository = ChatRepository(db)

# -----------------------------------------
# Create a test session
# -----------------------------------------

session = repository.create_session(user_id=1, title="Memory Test")

# -----------------------------------------
# Insert some messages
# -----------------------------------------

repository.save_message(session.id, MessageRole.USER.value, "Hello")

repository.save_message(session.id, MessageRole.ASSISTANT.value, "Hi!")

repository.save_message(session.id, MessageRole.USER.value, "Tell me about Python.")

repository.save_message(
    session.id, MessageRole.ASSISTANT.value, "Python is a programming language."
)

# -----------------------------------------
# Test Conversation Memory
# -----------------------------------------

memory = ConversationMemory(repository)

history = memory.format_history(session.id)

print(history)

db.close()
