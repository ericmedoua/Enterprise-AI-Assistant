from unittest.mock import Mock, patch

from app.ai.evaluation.evaluation_deployment_gate_cli import (
    run_evaluation_deployment_gate,
)


def test_run_evaluation_deployment_gate_returns_zero_when_allowed(capsys):
    repository = Mock()

    gate = Mock(
        allowed=True,
        exit_code=0,
        message="Deployment allowed: evaluation checks passed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_deployment_gate_cli."
        "build_evaluation_deployment_gate",
        return_value=gate,
    ) as mock_build_gate:
        result = run_evaluation_deployment_gate(repository)

    assert result == 0

    captured = capsys.readouterr()

    assert captured.out.strip() == ("Deployment allowed: evaluation checks passed.")

    mock_build_gate.assert_called_once_with(repository)


def test_run_evaluation_deployment_gate_returns_one_when_blocked(capsys):
    repository = Mock()

    gate = Mock(
        allowed=False,
        exit_code=1,
        message="Deployment blocked: evaluation checks failed.",
    )

    with patch(
        "app.ai.evaluation.evaluation_deployment_gate_cli."
        "build_evaluation_deployment_gate",
        return_value=gate,
    ) as mock_build_gate:
        result = run_evaluation_deployment_gate(repository)

    assert result == 1

    captured = capsys.readouterr()

    assert captured.out.strip() == ("Deployment blocked: evaluation checks failed.")

    mock_build_gate.assert_called_once_with(repository)
