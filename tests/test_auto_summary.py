from app.database.session import SessionLocal

from app.repositories.chat_repository import ChatRepository

from app.ai.memory.conversation_summarizer import (
    ConversationSummarizer,
)

db = SessionLocal()

repo = ChatRepository(db)

summarizer = ConversationSummarizer(repo)

summary = summarizer.summarize_session(1)

print(summary)

print()

print(repo.get_summary(1))
