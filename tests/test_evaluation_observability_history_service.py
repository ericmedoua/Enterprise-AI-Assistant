from unittest.mock import Mock

from datetime import datetime, timezone

from app.ai.evaluation.evaluation_history import (
    build_evaluation_history,
)
from app.ai.evaluation.evaluation_observability_history_service import (
    get_evaluation_observability_history,
)


def test_get_evaluation_observability_history_uses_repository():
    repository = Mock()

    runs = [
        Mock(
            id=2,
            created_at=datetime(2026, 8, 30, 13, 0, tzinfo=timezone.utc),
            dataset_name="rag-evaluation-v1",
            llm_model="openai/gpt-oss-120b",
            embedding_model="all-MiniLM-L6-v2",
            git_commit="a" * 40,
            status="completed",
            started_at=datetime(2026, 8, 30, 13, 0, tzinfo=timezone.utc),
            completed_at=datetime(2026, 8, 30, 13, 0, 10, tzinfo=timezone.utc),
            total_cases=2,
            retrieval_hit_rate=1.0,
            average_groundedness=1.0,
            average_semantic_relevance=0.6,
            average_source_count=1.0,
            overall_pass_rate=1.0,
            quality_gate_passed=True,
        ),
    ]

    repository.list_runs.return_value = runs

    result = get_evaluation_observability_history(repository)

    assert result == build_evaluation_history(runs)
    repository.list_runs.assert_called_once()
