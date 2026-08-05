from unittest.mock import MagicMock
from app.ai.chat.chatbot_service import ChatbotService


def test_magic_mock_example():

    llm = MagicMock()

    llm.invoke.return_value = "Mock response"

    response = llm.invoke("Hello")

    assert response == "Mock response"

    llm.invoke.assert_called_once()

    llm.invoke.assert_called_with("Hello")


def test_multiple_mocks():

    llm = MagicMock()

    retriever = MagicMock()

    retriever.invoke.return_value = ["Python is a programming language."]

    llm.invoke.return_value = "Python is a programming language."

    documents = retriever.invoke("What is Python?")

    answer = llm.invoke(documents)

    assert answer == "Python is a programming language."

    retriever.invoke.assert_called_once()

    llm.invoke.assert_called_once()


def test_chatbot_service_uses_chain():

    fake_chain = MagicMock()

    fake_chain.invoke.return_value = "Python is awesome."

    service = ChatbotService(
        chain=fake_chain,
    )

    answer = service.ask(
        "What is Python?",
        [],
    )

    assert answer == "Python is awesome."

    fake_chain.invoke.assert_called_once_with(
        {
            "question": "What is Python?",
            "history": [],
        }
    )


def test_chatbot_service_with_mocked_dependencies():

    fake_retriever = MagicMock()

    fake_llm = MagicMock()

    fake_chain = MagicMock()

    fake_chain.invoke.return_value = "Paris is the capital of France."

    service = ChatbotService(
        retriever=fake_retriever,
        llm=fake_llm,
        chain=fake_chain,
    )

    response = service.ask(
        "What is the capital of France?",
        [],
    )

    assert response == "Paris is the capital of France."

    fake_chain.invoke.assert_called_once_with(
        {
            "question": "What is the capital of France?",
            "history": [],
        }
    )

    assert service.retriever is fake_retriever
    assert service.llm is fake_llm
    assert service.chain is fake_chain
