from app.core.logger import app_logger


def log_evaluation_created(
    run_id: int,
    dataset_name: str,
) -> None:
    app_logger.info(
        f"Evaluation run created | run_id={run_id} | dataset={dataset_name}"
    )


def log_evaluation_started(
    run_id: int,
) -> None:
    app_logger.info(f"Evaluation run started | run_id={run_id}")


def log_evaluation_completed(
    run_id: int,
    duration_seconds: float | None,
    retrieval_hit_rate: float,
    groundedness: float,
    semantic_relevance: float,
    overall_pass_rate: float,
    quality_gate_passed: bool,
) -> None:
    app_logger.info(
        "Evaluation run completed | "
        f"run_id={run_id} | "
        f"duration={duration_seconds} | "
        f"retrieval_hit_rate={retrieval_hit_rate:.4f} | "
        f"groundedness={groundedness:.4f} | "
        f"semantic_relevance={semantic_relevance:.4f} | "
        f"overall_pass_rate={overall_pass_rate:.4f} | "
        f"quality_gate_passed={quality_gate_passed}"
    )


def log_evaluation_failed(
    run_id: int,
) -> None:
    app_logger.error(f"Evaluation run failed | run_id={run_id}")


def log_evaluation_remediated(
    run_id: int,
) -> None:
    app_logger.warning(f"Stale evaluation run remediated | run_id={run_id}")
