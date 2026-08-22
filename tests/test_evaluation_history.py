import pytest

from unittest.mock import Mock

from app.ai.evaluation.evaluation_history import (
    compare_latest_runs,
)


def test_compare_latest_runs():
    repository = Mock()

    previous = Mock(
        id=1,
        retrieval_hit_rate=1.0,
        average_groundedness=1.0,
        average_semantic_relevance=0.60,
        average_source_count=1.0,
        overall_pass_rate=1.0,
    )

    current = Mock(
        id=2,
        retrieval_hit_rate=1.0,
        average_groundedness=0.75,
        average_semantic_relevance=0.65,
        average_source_count=1.0,
        overall_pass_rate=0.50,
    )

    repository.get_latest_run.return_value = current
    repository.get_previous_run.return_value = previous

    result = compare_latest_runs(repository)

    assert result is not None
    assert result.groundedness_delta == pytest.approx(-0.25)
    assert result.semantic_relevance_delta == pytest.approx(0.05)
    assert result.overall_pass_rate_delta == pytest.approx(-0.50)


def test_compare_latest_runs_returns_none_without_current():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = compare_latest_runs(repository)

    assert result is None


def test_compare_latest_runs_returns_none_without_previous():
    repository = Mock()

    current = Mock(id=1)

    repository.get_latest_run.return_value = current
    repository.get_previous_run.return_value = None

    result = compare_latest_runs(repository)

    assert result is None
