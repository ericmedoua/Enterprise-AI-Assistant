from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.ai.evaluation.evaluation_trend_service import (
    build_latest_evaluation_trends,
)


def make_run(
    run_id: int,
    retrieval_hit_rate: float = 1.0,
    groundedness: float = 1.0,
    semantic_relevance: float = 0.8,
    source_count: float = 1.0,
    pass_rate: float = 1.0,
):
    run = Mock()

    run.id = run_id
    run.created_at = datetime(
        2026,
        9,
        1,
        tzinfo=timezone.utc,
    )

    run.retrieval_hit_rate = retrieval_hit_rate
    run.average_groundedness = groundedness
    run.average_semantic_relevance = semantic_relevance
    run.average_source_count = source_count
    run.overall_pass_rate = pass_rate

    return run


def test_build_latest_evaluation_trends():
    repository = Mock()

    previous = make_run(
        run_id=1,
        retrieval_hit_rate=0.8,
        groundedness=0.8,
        semantic_relevance=0.7,
        source_count=1.0,
        pass_rate=0.8,
    )

    current = make_run(
        run_id=2,
        retrieval_hit_rate=1.0,
        groundedness=0.9,
        semantic_relevance=0.8,
        source_count=2.0,
        pass_rate=1.0,
    )

    repository.list_runs.return_value = [
        current,
        previous,
    ]

    result = build_latest_evaluation_trends(repository)

    assert len(result) == 5

    assert result[0].metric_name == "retrieval_hit_rate"
    assert result[0].previous_value == 0.8
    assert result[0].current_value == 1.0
    assert result[0].delta == pytest.approx(0.2)
    assert result[0].direction == "improving"

    assert result[1].metric_name == "average_groundedness"
    assert result[1].direction == "improving"

    assert result[2].metric_name == "average_semantic_relevance"
    assert result[2].direction == "improving"

    assert result[3].metric_name == "average_source_count"
    assert result[3].direction == "improving"

    assert result[4].metric_name == "overall_pass_rate"
    assert result[4].direction == "improving"

    repository.list_runs.assert_called_once()


def test_build_latest_evaluation_trends_declining():
    repository = Mock()

    previous = make_run(
        run_id=1,
        retrieval_hit_rate=1.0,
        groundedness=1.0,
        semantic_relevance=0.9,
        source_count=2.0,
        pass_rate=1.0,
    )

    current = make_run(
        run_id=2,
        retrieval_hit_rate=0.8,
        groundedness=0.7,
        semantic_relevance=0.6,
        source_count=1.0,
        pass_rate=0.5,
    )

    repository.list_runs.return_value = [
        current,
        previous,
    ]

    result = build_latest_evaluation_trends(repository)

    assert all(trend.direction == "declining" for trend in result)


def test_build_latest_evaluation_trends_with_one_run():
    repository = Mock()

    repository.list_runs.return_value = [
        make_run(run_id=1),
    ]

    result = build_latest_evaluation_trends(repository)

    assert result == []


def test_build_latest_evaluation_trends_with_no_runs():
    repository = Mock()

    repository.list_runs.return_value = []

    result = build_latest_evaluation_trends(repository)

    assert result == []
