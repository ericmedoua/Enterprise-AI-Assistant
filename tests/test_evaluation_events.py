from unittest.mock import patch

from app.ai.evaluation.evaluation_events import (
    log_evaluation_created,
    log_evaluation_completed,
)


@patch("app.ai.evaluation.evaluation_events.app_logger")
def test_log_evaluation_completed(
    mock_logger,
):
    log_evaluation_completed(
        run_id=42,
        duration_seconds=18.5,
        retrieval_hit_rate=1.0,
        groundedness=0.95,
        semantic_relevance=0.72,
        overall_pass_rate=0.80,
        quality_gate_passed=False,
    )

    mock_logger.info.assert_called_once_with(
        "Evaluation run completed | "
        "run_id=42 | "
        "duration=18.5 | "
        "retrieval_hit_rate=1.0000 | "
        "groundedness=0.9500 | "
        "semantic_relevance=0.7200 | "
        "overall_pass_rate=0.8000 | "
        "quality_gate_passed=False"
    )
