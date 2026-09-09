from app.ai.evaluation.evaluation_ci_report import EvaluationCIReport


def format_evaluation_ci_report(report: EvaluationCIReport) -> str:
    quality_gate = "PASSED" if report.quality_gate_passed else "FAILED"
    deployment = "ALLOWED" if report.deployment_ready else "BLOCKED"

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
        "========================================"
    )
