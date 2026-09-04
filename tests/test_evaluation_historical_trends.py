from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.ai.evaluation.evaluation_historical_trends import (
    build_historical_evaluation_trends,
    build_historical_metric_trend,
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


def test_build_historical_metric_trend():
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

    result = build_historical_metric_trend(
        metric_name="retrieval_hit_rate",
        runs=[newer, older],
    )

    assert result.metric_name == "retrieval_hit_rate"
    assert len(result.points) == 2

    assert result.points[0].run_id == 1
    assert result.points[0].value == 0.8

    assert result.points[1].run_id == 2
    assert result.points[1].value == 1.0

    assert result.direction == "improving"


def test_build_historical_metric_trend_declining():
    older = make_run(
        run_id=1,
        created_at=datetime(
            2026,
            8,
            1,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=1.0,
        groundedness=1.0,
        semantic_relevance=0.9,
        source_count=2.0,
        pass_rate=1.0,
    )

    newer = make_run(
        run_id=2,
        created_at=datetime(
            2026,
            8,
            2,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=0.8,
        groundedness=0.7,
        semantic_relevance=0.6,
        source_count=1.0,
        pass_rate=0.5,
    )

    result = build_historical_metric_trend(
        metric_name="retrieval_hit_rate",
        runs=[newer, older],
    )

    assert result.direction == "declining"


def test_build_historical_metric_trend_stable():
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
        pass_rate=0.8,
    )

    newer = make_run(
        run_id=2,
        created_at=datetime(
            2026,
            8,
            2,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=0.8005,
        groundedness=0.8005,
        semantic_relevance=0.7005,
        source_count=1.0005,
        pass_rate=0.8005,
    )

    result = build_historical_metric_trend(
        metric_name="retrieval_hit_rate",
        runs=[newer, older],
    )

    assert result.direction == "stable"


def test_build_historical_metric_trend_with_one_run():
    run = make_run(
        run_id=1,
        created_at=datetime(
            2026,
            8,
            1,
            tzinfo=timezone.utc,
        ),
        retrieval_hit_rate=1.0,
        groundedness=1.0,
        semantic_relevance=0.8,
        source_count=1.0,
        pass_rate=1.0,
    )

    result = build_historical_metric_trend(
        metric_name="retrieval_hit_rate",
        runs=[run],
    )

    assert len(result.points) == 1
    assert result.direction == "stable"


def test_build_historical_metric_trend_empty():
    result = build_historical_metric_trend(
        metric_name="retrieval_hit_rate",
        runs=[],
    )

    assert result.points == []
    assert result.direction == "stable"


def test_build_historical_evaluation_trends():
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

    result = build_historical_evaluation_trends([newer, older])

    assert len(result) == 5

    assert all(trend.direction == "improving" for trend in result)
