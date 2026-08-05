from app.ai.prompts.prompt_builder import (
    PromptBuilder,
)

builder = PromptBuilder()

prompt = builder.build(
    question="What is Python?",
    history="""
User: Hello

Assistant: Hi!
""",
    context="""
Python is a programming language.
""",
)

print(prompt)
