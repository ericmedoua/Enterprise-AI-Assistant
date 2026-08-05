# app/observability/observability_service.py

from app.observability.logger import logger


class ObservabilityService:
    def log_metrics(
        self,
        metrics,
    ):

        logger.info(
            (
                "\n"
                "Database : %.2f ms\n"
                "Memory   : %.2f ms\n"
                "Retriever: %.2f ms\n"
                "Documents: %d\n"
                "LLM      : %.2f ms\n"
                "Total    : %.2f ms"
            ),
            metrics.database_ms,
            metrics.memory_ms,
            metrics.retrieval_ms,
            metrics.documents_ms,
            metrics.llm_ms,
            metrics.total_ms,
        )
