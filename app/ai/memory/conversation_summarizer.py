from app.ai.memory.summary_formatter import (
    format_for_summary,
)

from app.ai.memory.summary_service import (
    SummaryService,
)


class ConversationSummarizer:
    def __init__(
        self,
        repository,
    ):

        self.repository = repository

        self.summary_service = SummaryService()

    def summarize_session(
        self,
        session_id: int,
    ):

        messages = self.repository.get_messages(
            session_id,
        )

        conversation = format_for_summary(
            messages,
        )

        summary = self.summary_service.summarize(
            conversation,
        )

        self.repository.update_summary(
            session_id,
            summary,
        )

        return summary
