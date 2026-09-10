from unittest import result
from unittest.mock import Mock, patch

import pytest

from app.ai.evaluation.evaluation_ci_report_service import (
    build_evaluation_ci_report_for_repository,
)


def test_build_ci_report_when_deployment_is_ready():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=True,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        average_source_count=1.5,
        overall_pass_rate=0.85,
    )

    repository.get_latest_run.return_value = latest_run

    readiness = Mock(
        ready=True,
        status="ready",
        reason="Evaluation quality checks passed.",
    )

    previous_run = Mock(
        retrieval_hit_rate=0.9,
        average_groundedness=0.8,
        average_semantic_relevance=0.5,
        average_source_count=1.0,
        overall_pass_rate=0.8,
    )

    repository.get_previous_run.return_value = previous_run

    with patch(
        "app.ai.evaluation.evaluation_ci_report_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ) as mock_build_readiness:
        result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "passed"
    assert result.quality_gate_passed is True
    assert result.deployment_ready is True
    assert result.message == ("Evaluation passed and deployment is allowed.")

    assert result.retrieval_hit_rate == 1.0
    assert result.average_groundedness == 0.9
    assert result.average_semantic_relevance == 0.8
    assert result.overall_pass_rate == 0.85

    assert result.comparison is not None
    assert result.comparison.retrieval_hit_rate_delta == pytest.approx(0.1)
    assert result.comparison.groundedness_delta == pytest.approx(0.1)
    assert result.comparison.semantic_relevance_delta == pytest.approx(0.3)
    assert result.comparison.source_count_delta == pytest.approx(0.5)
    assert result.comparison.overall_pass_rate_delta == pytest.approx(0.05)

    mock_build_readiness.assert_called_once_with(repository)


def test_build_ci_report_when_quality_gate_fails():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=False,
        retrieval_hit_rate=0.8,
        average_groundedness=0.7,
        average_semantic_relevance=0.6,
        average_source_count=1.5,
        overall_pass_rate=0.5,
    )

    repository.get_latest_run.return_value = latest_run
    repository.get_previous_run.return_value = None

    readiness = Mock(
        ready=False,
        status="blocked",
        reason="The evaluation quality gate failed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_ci_report_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ):
        result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "failed"
    assert result.quality_gate_passed is False
    assert result.deployment_ready is False
    assert result.message == ("Evaluation quality gate failed.")

    assert result.retrieval_hit_rate == 0.8
    assert result.average_groundedness == 0.7
    assert result.average_semantic_relevance == 0.6
    assert result.overall_pass_rate == 0.5


def test_build_ci_report_when_no_evaluation_exists():
    repository = Mock()

    repository.get_latest_run.return_value = None

    result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "failed"
    assert result.quality_gate_passed is False
    assert result.deployment_ready is False

    assert result.retrieval_hit_rate == 0.0
    assert result.average_groundedness == 0.0
    assert result.average_semantic_relevance == 0.0
    assert result.overall_pass_rate == 0.0


def test_build_ci_report_without_previous_run():
    repository = Mock()

    latest_run = Mock(
        quality_gate_passed=True,
        retrieval_hit_rate=1.0,
        average_groundedness=0.9,
        average_semantic_relevance=0.8,
        overall_pass_rate=0.95,
    )

    repository.get_latest_run.return_value = latest_run
    repository.get_previous_run.return_value = None

    readiness = Mock(
        ready=True,
        status="ready",
        reason="Evaluation quality checks passed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_ci_report_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ):
        result = build_evaluation_ci_report_for_repository(repository)

    assert result.status == "passed"
    assert result.quality_gate_passed is True
    assert result.deployment_ready is True
    assert result.comparison is None
