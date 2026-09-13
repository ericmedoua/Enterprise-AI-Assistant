from app.repositories.chat_repository import ChatRepository


def test_chat_repository(db, test_session):
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

    messages = repository.get_messages(test_session.id)

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi!"
