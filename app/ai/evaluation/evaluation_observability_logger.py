from app.ai.evaluation.evaluation_observability import (
    EvaluationObservabilityEvent,
    evaluation_event_payload,
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


def log_evaluation_event(
    event: EvaluationObservabilityEvent,
) -> None:
    payload = evaluation_event_payload(event)

    app_logger.info(
        "RAG evaluation completed | "
        f"event={payload['event']} "
        f"dataset={payload['dataset']} "
        f"quality_gate_passed={payload['quality_gate_passed']} "
        f"retrieval_hit_rate={payload['retrieval_hit_rate']:.4f} "
        f"groundedness={payload['average_groundedness']:.4f} "
        f"semantic_relevance={payload['average_semantic_relevance']:.4f} "
        f"overall_pass_rate={payload['overall_pass_rate']:.4f}"
    )
