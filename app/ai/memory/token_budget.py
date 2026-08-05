from app.core.constants import (
    MAX_MEMORY_TOKENS,
)


class TokenBudgetManager:
    def __init__(
        self,
        max_tokens: int = MAX_MEMORY_TOKENS,
    ):

        self.max_tokens = max_tokens

    def estimate_tokens(
        self,
        text: str,
    ) -> int:
        """
        Simple estimation:
        ~1 token ≈ 4 characters
        """

        return max(
            1,
            len(text) // 4,
        )

    def select_messages(
        self,
        messages,
    ):

        selected = []

        total_tokens = 0

        for message in reversed(messages):
            tokens = self.estimate_tokens(
                message.content,
            )

            if total_tokens + tokens > self.max_tokens:
                break

            selected.append(
                message,
            )

            total_tokens += tokens

        selected.reverse()

        return selected
