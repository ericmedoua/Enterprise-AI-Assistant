from app.ai.memory.memory_snapshot import MemorySnapshot
from app.ai.memory.message_formatter import format_chat_history
from app.ai.memory.token_budget import TokenBudgetManager
import asyncio


class MemoryManager:
    def __init__(
        self,
        repository,
    ):
        self.repository = repository

        self.token_budget = TokenBudgetManager()

    def load(
        self,
        session_id: int,
    ):

        summary = self.repository.get_summary(
            session_id,
        )

        messages = self.repository.get_messages(
            session_id,
        )

        messages = self.token_budget.select_messages(
            messages,
        )

        recent = format_chat_history(
            messages,
        )

        return MemorySnapshot(
            summary=summary,
            recent_messages=recent,
        )
    async def aload(
        self,
        session_id: int,
    ):
        return await asyncio.to_thread(
            self.load,
            session_id,
        )
