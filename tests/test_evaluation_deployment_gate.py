from app.ai.evaluation.evaluation_deployment_gate import (
    evaluate_deployment_gate,
)


def test_deployment_gate_allows_ready_evaluation():
    result = evaluate_deployment_gate(ready=True)

    assert result.allowed is True
    assert result.exit_code == 0
    assert result.message == ("Deployment allowed: evaluation checks passed.")


def test_deployment_gate_blocks_failed_evaluation():
    result = evaluate_deployment_gate(ready=False)

    assert result.allowed is False
    assert result.exit_code == 1
    assert result.message == ("Deployment blocked: evaluation checks failed.")
