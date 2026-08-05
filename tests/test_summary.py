from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)

from app.ai.memory.summary_formatter import (
    format_for_summary,
)

from app.ai.memory.summary_service import (
    SummaryService,
)

messages = [
    HumanMessage(content="Explain dependency injection."),
    AIMessage(content="Dependency injection allows Spring to manage object creation."),
    HumanMessage(content="Explain Spring Beans."),
    AIMessage(content="Spring Beans are managed by the IoC container."),
]

conversation = format_for_summary(messages)

service = SummaryService()

summary = service.summarize(conversation)

print(summary)
