from langchain_core.messages import (
    HumanMessage,
)

from app.ai.memory.token_budget import (
    TokenBudgetManager,
)

manager = TokenBudgetManager(
    max_tokens=50,
)

messages = [
    HumanMessage(
        content="Hello",
    ),
    HumanMessage(
        content="A" * 100,
    ),
    HumanMessage(
        content="B" * 150,
    ),
    HumanMessage(
        content="C" * 200,
    ),
]

selected = manager.select_messages(
    messages,
)

print()

print(
    "Selected Messages:",
)

for message in selected:
    print(
        len(message.content),
    )
