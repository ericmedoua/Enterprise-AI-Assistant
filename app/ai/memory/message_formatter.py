from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage

from app.models.message import Message
from app.core.constants import (
    USER_ROLE,
    ASSISTANT_ROLE,
)


def format_chat_history(
    messages: list[Message],
):

    history = []

    for message in messages:
        if message.role == USER_ROLE:
            history.append(HumanMessage(content=message.content))

        elif message.role == ASSISTANT_ROLE:
            history.append(AIMessage(content=message.content))

    return history
