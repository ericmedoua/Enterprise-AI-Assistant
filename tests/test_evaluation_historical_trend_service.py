from datetime import datetime, timezone
from unittest.mock import Mock

from app.ai.evaluation.evaluation_historical_trend_service import (
    build_evaluation_historical_trends,
)


def make_run(
    run_id: int,
    created_at: datetime,
    retrieval_hit_rate: float,
    groundedness: float,
    semantic_relevance: float,
    source_count: float,
    pass_rate: float,
):
    run = Mock()

    run.id = run_id
    run.created_at = created_at

    run.retrieval_hit_rate = retrieval_hit_rate
    run.average_groundedness = groundedness
    run.average_semantic_relevance = semantic_relevance
    run.average_source_count = source_count
    run.overall_pass_rate = pass_rate

    return run


def test_build_evaluation_historical_trends():
    repository = Mock()

    older = make_run(
        run_id=1,
        created_at=datetime(
            2026,
            8,
            1,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=0.8,
        groundedness=0.8,
        semantic_relevance=0.7,
        source_count=1.0,
        pass_rate=0.5,
    )

    newer = make_run(
        run_id=2,
        created_at=datetime(
            2026,
            8,
            2,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=1.0,
        groundedness=0.9,
        semantic_relevance=0.8,
        source_count=2.0,
        pass_rate=1.0,
    )

    repository.list_runs.return_value = [
        newer,
        older,
    ]

    result = build_evaluation_historical_trends(repository)

    assert len(result) == 5

    assert result[0].metric_name == ("retrieval_hit_rate")
    assert result[0].direction == "improving"
    assert result[0].points[0].run_id == 1
    assert result[0].points[1].run_id == 2

    assert result[1].metric_name == ("average_groundedness")

    assert result[2].metric_name == ("average_semantic_relevance")

    assert result[3].metric_name == ("average_source_count")

    assert result[4].metric_name == ("overall_pass_rate")

    repository.list_runs.assert_called_once_with(
        limit=None,
    )


def test_build_evaluation_historical_trends_empty():
    repository = Mock()
    repository.list_runs.return_value = []

    result = build_evaluation_historical_trends(repository)

    assert len(result) == 5

    assert all(trend.points == [] for trend in result)

    assert all(trend.direction == "stable" for trend in result)

    repository.list_runs.assert_called_once_with(
        limit=None,
    )


def test_build_evaluation_historical_trends_with_limit():
    repository = Mock()

    repository.list_runs.return_value = []

    result = build_evaluation_historical_trends(
        repository,
        limit=10,
    )

    assert len(result) == 5

    repository.list_runs.assert_called_once_with(
        limit=10,
    )
