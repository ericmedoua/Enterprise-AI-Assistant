from app.ai.chains.rag_chain import build_rag_chain
from app.ai.memory.conversation_summarizer import ConversationSummarizer
from app.ai.memory.memory_manager import MemoryManager
from app.core.constants import MessageRole, SUMMARY_TRIGGER_MESSAGES
from app.observability.request_trace import RequestTrace
from app.repositories.chat_repository import ChatRepository
import asyncio


class ConversationService:
    def __init__(
        self,
        repository,
        retriever,
        llm,
        observability,
    ):
        self.repository = repository
        self.retriever = retriever
        self.llm = llm
        self.observability = observability
        self.memory_manager = MemoryManager(repository)
        self.summarizer = ConversationSummarizer(repository)

    async def ask(
        self,
        session_id: int,
        question: str,
    ):

        trace = RequestTrace()

        self.rag_chain = build_rag_chain(
            retriever=self.retriever,
            llm=self.llm,
            metrics=trace.metrics,
        )

        self.repository.save_message(
            session_id,
            MessageRole.USER.value,
            question,
        )

        trace.start_stage()

        snapshot = self.memory_manager.load(session_id)

        history = snapshot.recent_messages
        summary = snapshot.summary

        trace.end_memory()

        trace.end_database()

        answer = ""

        trace.start_stage()

        async for chunk in self.rag_chain.astream(
            {
                "question": question,
                "history": history,
                "summary": summary,
            }
        ):
            answer += chunk
            yield chunk

        trace.end_llm()

        self.repository.save_message(
            session_id,
            MessageRole.ASSISTANT.value,
            answer,
        )

        metrics = trace.finish()

        print()

        self.observability.log_metrics(
            metrics,
        )

        """
        print("=" * 60)

        print("REQUEST METRICS")

        print("=" * 60)

        print(f"Database : {metrics.database_ms:.2f} ms")

        print(f"Memory   : {metrics.memory_ms:.2f} ms")

        print(f"Retriever: {metrics.retrieval_ms:.2f} ms")

        print(f"Documents: {metrics.retrieved_documents}")

        print(f"LLM      : {metrics.llm_ms:.2f} ms")

        print(f"Total    : {metrics.total_ms:.2f} ms")

        print("=" * 60)

        print()
        """

        message_count = self.repository.count_messages(
            session_id,
        )

        if message_count >= SUMMARY_TRIGGER_MESSAGES:
            self.summarizer.summarize_session(
                session_id,
            )
            self.summarizer = ConversationSummarizer(self.repository)

        memory_task = asyncio.create_task(
            self.memory_manager.aload(session_id)
        )

        snapshot = await memory_task
