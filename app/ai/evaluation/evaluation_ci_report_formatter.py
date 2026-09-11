from app.ai.evaluation.evaluation_ci_report import EvaluationCIReport
from app.ai.evaluation.evaluation_comparison_report import (
    format_evaluation_comparison,
)


def format_regression_details(
    regressions,
) -> str:
    if not regressions:
        return ""

    lines = [
        "",
        "Regression Details",
        "------------------",
    ]

    for regression in regressions:
        lines.append(
            f"- {regression.metric_name}: "
            f"{regression.delta:+.2%} "
            f"({regression.severity})"
        )

    return "\n".join(lines)


def format_evaluation_ci_report(
    report: EvaluationCIReport, include_comparison: bool = False
) -> str:
    quality_gate = "PASSED" if report.quality_gate_passed else "FAILED"
    deployment = "ALLOWED" if report.deployment_ready else "BLOCKED"
    comparison_section = ""

    if include_comparison and report.comparison is not None:
        comparison_section = (
            "\n" + format_evaluation_comparison(report.comparison) + "\n"
        )

    regression_section = format_regression_details(report.regressions)

    return (
        "========================================\n"
        "RAG EVALUATION CI REPORT\n"
        "========================================\n"
        f"Status: {report.status.upper()}\n"
        f"Quality gate: {quality_gate}\n"
        f"Deployment: {deployment}\n"
        "\n"
        "Evaluation Metrics\n"
        "------------------\n"
        f"Retrieval hit rate: {report.retrieval_hit_rate:.2%}\n"
        f"Groundedness: {report.average_groundedness:.2%}\n"
        f"Semantic relevance: {report.average_semantic_relevance:.2%}\n"
        f"Overall pass rate: {report.overall_pass_rate:.2%}\n"
        "\n"
        f"Reason: {report.message}\n"
        f"{comparison_section}"
        f"{regression_section}\n"
        "========================================"
    )
