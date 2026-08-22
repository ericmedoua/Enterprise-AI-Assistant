from app.ai.evaluation.experiment_gate import (
    ExperimentGateResult,
)


def format_experiment_gate_result(
    result: ExperimentGateResult,
) -> str:
    return "\n".join(
        [
            "EXPERIMENT QUALITY GATE",
            "=======================",
            (f"Retrieval:          {'PASS' if result.retrieval_passed else 'FAIL'}"),
            (f"Groundedness:       {'PASS' if result.groundedness_passed else 'FAIL'}"),
            (
                "Semantic relevance: "
                f"{'PASS' if result.semantic_relevance_passed else 'FAIL'}"
            ),
            (
                "Overall pass rate:  "
                f"{'PASS' if result.overall_pass_rate_passed else 'FAIL'}"
            ),
            "",
            f"DECISION: {'ACCEPT' if result.passed else 'REJECT'}",
        ]
    )
