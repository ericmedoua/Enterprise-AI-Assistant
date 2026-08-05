from app.ai.memory.message_formatter import (
    format_chat_history,
)
from app.models.message import Message
from app.core.constants import (
    USER_ROLE,
    ASSISTANT_ROLE,
)

messages = [
    Message(role=USER_ROLE, content="Hello"),
    Message(role=ASSISTANT_ROLE, content="Hi!"),
]

history = format_chat_history(messages)

print(history)
