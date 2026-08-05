from dataclasses import dataclass

from langchain_core.messages import BaseMessage


@dataclass
class MemorySnapshot:
    summary: str

    recent_messages: list[BaseMessage]

    @property
    def has_summary(self):

        return bool(self.summary.strip())
