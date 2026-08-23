from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)


def format_evaluation_snapshot(
    snapshot: EvaluationSnapshot,
) -> str:
    report = snapshot.report
    gate = snapshot.quality_gate

    lines = [
        "RAG EVALUATION SNAPSHOT",
        "=======================",
        f"Dataset: {snapshot.dataset_name}",
        "",
        f"Cases: {report.total_cases}",
        f"Retrieval hit rate: {report.retrieval_hit_rate:.2%}",
        f"Groundedness: {report.average_groundedness:.2%}",
        (f"Semantic relevance: {report.average_semantic_relevance:.2%}"),
        f"Average sources: {report.average_source_count:.2f}",
        f"Overall pass rate: {report.overall_pass_rate:.2%}",
        "",
        (f"Quality gate: {'PASS' if gate.passed else 'FAIL'}"),
    ]

    if snapshot.comparison is not None:
        comparison = snapshot.comparison

        lines.extend(
            [
                "",
                "Historical Delta",
                "----------------",
                (f"Retrieval: {comparison.retrieval_hit_rate_delta:+.2%}"),
                (f"Groundedness: {comparison.groundedness_delta:+.2%}"),
                (f"Semantic relevance: {comparison.semantic_relevance_delta:+.2%}"),
                (f"Overall pass rate: {comparison.overall_pass_rate_delta:+.2%}"),
            ]
        )

    return "\n".join(lines)
