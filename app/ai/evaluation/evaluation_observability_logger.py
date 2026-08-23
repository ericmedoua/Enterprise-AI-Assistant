from app.ai.evaluation.evaluation_observability import (
    EvaluationObservabilityEvent,
)

from app.core.logger import app_logger


def log_evaluation_event(
    event: EvaluationObservabilityEvent,
) -> None:
    """
    Emit a structured RAG evaluation event using
    the application's existing logger.
    """

    app_logger.info(f"RAG evaluation completed | {event.to_dict()}")
