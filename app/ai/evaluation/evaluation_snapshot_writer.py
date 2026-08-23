import json
from pathlib import Path

from app.ai.evaluation.evaluation_snapshot import (
    EvaluationSnapshot,
)


def write_evaluation_snapshot(
    snapshot: EvaluationSnapshot,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            snapshot.to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )

    return path
