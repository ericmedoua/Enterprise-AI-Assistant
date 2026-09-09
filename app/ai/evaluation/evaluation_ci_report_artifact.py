from pathlib import Path

from app.ai.evaluation.evaluation_ci_report import (
    EvaluationCIReport,
)
from app.ai.evaluation.evaluation_ci_report_formatter import (
    format_evaluation_ci_report,
)


def write_evaluation_ci_report(
    report: EvaluationCIReport,
    output_path: str = "artifacts/evaluation-ci-report.txt",
) -> Path:
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        format_evaluation_ci_report(report),
        encoding="utf-8",
    )

    return path
