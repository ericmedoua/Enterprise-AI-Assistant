from app.ai.evaluation.evaluation_metadata import (
    get_evaluation_metadata,
)
from app.ai.evaluation.evaluation_runner import (
    EvaluationRunner,
)
from app.ai.evaluation.evaluation_snapshot_report import (
    format_evaluation_snapshot,
)
from app.database.session import SessionLocal


def main() -> None:
    metadata = get_evaluation_metadata()

    db = SessionLocal()

    try:
        runner = EvaluationRunner(
            db=db,
            metadata=metadata,
        )

        result = runner.run()

        print(format_evaluation_snapshot(result.snapshot))

    finally:
        db.close()


if __name__ == "__main__":
    main()
