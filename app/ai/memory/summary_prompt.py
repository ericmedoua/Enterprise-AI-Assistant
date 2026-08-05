from langchain_core.prompts import ChatPromptTemplate


summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert conversation summarizer.

Your job is to summarize the conversation while preserving:

• technical decisions
• architecture choices
• user goals
• unresolved questions
• important facts

Do NOT include greetings.

Do NOT include small talk.

Keep the summary under 300 words.

Return only the summary.
""",
        ),
        (
            "human",
            """
Conversation:

{conversation}
""",
        ),
    ]
)
