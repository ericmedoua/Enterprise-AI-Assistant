from unittest.mock import patch

from app.ai.evaluation.evaluation_observability import (
    EvaluationObservabilityEvent,
)

from app.ai.evaluation.evaluation_observability_logger import (
    log_evaluation_event,
)


def test_log_evaluation_event():
    event = EvaluationObservabilityEvent(
        event_name="rag_evaluation_completed",
        dataset_name="rag-evaluation-v1",
        total_cases=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.75,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=0.50,
        quality_gate_passed=False,
        has_historical_comparison=True,
    )

    with patch(
        "app.ai.evaluation.evaluation_observability_logger.app_logger"
    ) as mock_logger:
        log_evaluation_event(event)

        mock_logger.info.assert_called_once()

        message = mock_logger.info.call_args[0][0]

        assert "RAG evaluation completed" in message

        assert "rag-evaluation-v1" in message

        assert "quality_gate_passed=False" in message

        assert "retrieval_hit_rate=1.0000" in message

        assert "groundedness=0.7500" in message

        assert "semantic_relevance=0.6000" in message

        assert "overall_pass_rate=0.5000" in message
