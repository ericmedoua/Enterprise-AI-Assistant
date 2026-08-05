from app.core.constants import MessageRole


async def handle_chat_session(
    repository, session, question: str, answer: str, prompt: str
):
    # Executable logic lives inside a function/method
    await repository.save_message(session.id, MessageRole.USER, question)
    await repository.save_message(session.id, MessageRole.ASSISTANT, answer)
    await repository.save_message(session.id, MessageRole.SYSTEM, prompt)
