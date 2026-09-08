from app.ai.evaluation.evaluation_deployment_gate_cli import (
    run_evaluation_deployment_gate,
)
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
from app.repositories.evaluation_repository import (
    EvaluationRepository,
)


def main() -> int:
    metadata = get_evaluation_metadata()

    db = SessionLocal()

    try:
        runner = EvaluationRunner(
            db=db,
            metadata=metadata,
        )

        result = runner.run()

        print(format_evaluation_snapshot(result.snapshot))

        repository = EvaluationRepository(db)

        return run_evaluation_deployment_gate(repository)

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
