from app.ai.evaluation.quality_gate import (
    QualityGateResult,
)


def format_quality_gate_result(
    result: QualityGateResult,
) -> str:
    lines = [
        "RAG QUALITY GATE",
        "================",
        f"Retrieval:         {'PASS' if result.retrieval_passed else 'FAIL'}",
        f"Groundedness:      {'PASS' if result.groundedness_passed else 'FAIL'}",
        f"Semantic Relevance:{'PASS' if result.semantic_relevance_passed else 'FAIL'}",
        f"Overall Pass Rate: {'PASS' if result.overall_passed else 'FAIL'}",
        "",
        f"FINAL: {'PASS' if result.passed else 'FAIL'}",
    ]

    return "\n".join(lines)
