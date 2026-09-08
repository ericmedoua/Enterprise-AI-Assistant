from app.ai.evaluation.evaluation_deployment_gate_service import (
    build_evaluation_deployment_gate,
)


def run_evaluation_deployment_gate(repository) -> int:
    gate = build_evaluation_deployment_gate(repository)

    print(gate.message)

    return gate.exit_code
