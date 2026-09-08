from pathlib import Path


def test_evaluation_workflow_exists():
    workflow = Path(".github/workflows/evaluation.yml")

    assert workflow.exists()


def test_evaluation_workflow_contains_evaluation_command():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "python -m app.ai.evaluation.cli" in content


def test_evaluation_workflow_runs_tests():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "pytest -q" in content


def test_evaluation_workflow_configures_postgres():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "postgres:16" in content
    assert "POSTGRES_DB: enterprise_ai_assistant" in content
    assert "DATABASE_HOST: 127.0.0.1" in content
    assert "DATABASE_PORT: 5432" in content


def test_evaluation_workflow_uses_github_secret_for_groq():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}" in content


def test_evaluation_workflow_uses_python_cache():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "cache: pip" in content


def test_evaluation_workflow_runs_database_migrations():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "alembic upgrade head" in content


def test_database_migrations_run_before_evaluation():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    migration_position = content.index("alembic upgrade head")
    evaluation_position = content.index("python -m app.ai.evaluation.cli")

    assert migration_position < evaluation_position


def test_evaluation_workflow_prepares_embedding_model():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "SentenceTransformer" in content
    assert "all-MiniLM-L6-v2" in content


def test_embedding_model_is_prepared_before_evaluation():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    model_position = content.index("SentenceTransformer")
    evaluation_position = content.index("python -m app.ai.evaluation.cli")

    assert model_position < evaluation_position


def test_evaluation_gate_does_not_allow_failure():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    assert "continue-on-error: true" not in content
    assert "|| true" not in content


def test_evaluation_gate_is_final_execution_step():
    workflow = Path(".github/workflows/evaluation.yml")

    content = workflow.read_text(encoding="utf-8")

    evaluation_position = content.index("python -m app.ai.evaluation.cli")

    workflow_after_evaluation = content[evaluation_position:]

    assert "continue-on-error: true" not in workflow_after_evaluation
