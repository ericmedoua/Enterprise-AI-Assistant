from app.ai.evaluation.evaluation_deployment_gate import (
    EvaluationDeploymentGate,
    evaluate_deployment_gate,
)
from app.ai.evaluation.evaluation_deployment_readiness_service import (
    build_evaluation_deployment_readiness,
)


def build_evaluation_deployment_gate(
    repository,
) -> EvaluationDeploymentGate:
    readiness = build_evaluation_deployment_readiness(repository)

    return evaluate_deployment_gate(
        ready=readiness.ready,
    )
