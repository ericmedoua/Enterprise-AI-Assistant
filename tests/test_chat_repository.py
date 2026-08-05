from app.repositories.chat_repository import ChatRepository

from app.database.session import SessionLocal


db = SessionLocal()

repository = ChatRepository(db)

session = repository.create_session(
    user_id=1,
    title="My First Chat",
)

print(session.id)

repository.save_message(session.id, "user", "Hello")

repository.save_message(session.id, "assistant", "Hi!")

messages = repository.get_messages(session.id)

for message in messages:
    print(message.role)

    print(message.content)
