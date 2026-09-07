from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_deployment_gate_service import (
    build_evaluation_deployment_gate,
)


def test_build_deployment_gate_when_ready():
    repository = Mock()

    readiness = Mock(
        ready=True,
        status="ready",
        reason="Evaluation quality checks passed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_deployment_gate_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ) as mock_build_readiness:
        result = build_evaluation_deployment_gate(repository)

    assert result.allowed is True
    assert result.exit_code == 0
    assert result.message == ("Deployment allowed: evaluation checks passed.")

    mock_build_readiness.assert_called_once_with(repository)


def test_build_deployment_gate_when_blocked():
    repository = Mock()

    readiness = Mock(
        ready=False,
        status="blocked",
        reason="The evaluation quality gate failed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_deployment_gate_service."
        "build_evaluation_deployment_readiness",
        return_value=readiness,
    ) as mock_build_readiness:
        result = build_evaluation_deployment_gate(repository)

    assert result.allowed is False
    assert result.exit_code == 1
    assert result.message == ("Deployment blocked: evaluation checks failed.")

    mock_build_readiness.assert_called_once_with(repository)
