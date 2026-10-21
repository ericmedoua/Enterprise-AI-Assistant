from unittest.mock import MagicMock

from app.api import chat


def test_chatbot_service_dependency_uses_user_scoped_retriever(monkeypatch):
    scoped_retriever = MagicMock()
    captured = {}

    def fake_chatbot_service(*, retriever):
        captured["retriever"] = retriever
        return "fake-chatbot-service"

    monkeypatch.setattr(
        chat,
        "ChatbotService",
        fake_chatbot_service,
    )

    result = chat.get_chatbot_service(retriever=scoped_retriever)

    assert result == "fake-chatbot-service"
    assert captured["retriever"] is scoped_retriever
