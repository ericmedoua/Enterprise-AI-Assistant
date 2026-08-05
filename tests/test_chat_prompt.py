from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage

from app.ai.prompts.chat_prompt import chat_prompt

prompt = chat_prompt.invoke(
    {
        "history": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi!"),
        ],
        "summary": "",
        "context": "Python is a programming language.",
        "question": "What is Python?",
    }
)

print(prompt)
