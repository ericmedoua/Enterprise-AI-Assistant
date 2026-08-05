from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)


def format_for_summary(messages):

    lines = []

    for message in messages:
        if isinstance(message, HumanMessage):
            role = "User"

        elif isinstance(message, AIMessage):
            role = "Assistant"

        elif isinstance(message, SystemMessage):
            role = "System"

        else:
            role = "Unknown"

        lines.append(f"{role}: {message.content}")

    return "\n".join(lines)
