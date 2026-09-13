from app.ai.memory.conversation_summarizer import ConversationSummarizer
from app.repositories.chat_repository import ChatRepository


def test_auto_summary(db, test_session):
    repository = ChatRepository(db)

    repository.save_message(
        test_session.id,
        "user",
        "Tell me about Python.",
    )

    repository.save_message(
        test_session.id,
        "assistant",
        "Python is a programming language used for many applications.",
    )

    summarizer = ConversationSummarizer(repository)

    summary = summarizer.summarize_session(test_session.id)
    stored_summary = repository.get_summary(test_session.id)

    assert summary is not None
    assert stored_summary is not None
    assert stored_summary == summary
