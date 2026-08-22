from unittest.mock import Mock

from app.ai.evaluation.historical_regression import (
    analyze_latest_regression,
)


def test_analyze_latest_regression():
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

    result = analyze_latest_regression(repository)

    assert result.comparison is not None
    assert result.regression is not None
    assert result.regression.regression_detected is True
    assert result.regression.groundedness_regression is True
    assert result.regression.overall_pass_rate_regression is True


def test_analyze_latest_regression_without_history():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = analyze_latest_regression(repository)

    assert result.comparison is None
    assert result.regression is None
