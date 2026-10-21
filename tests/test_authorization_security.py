from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.auth.authorization import require_admin
from app.auth.dependencies import get_current_user
from app.main import app


@pytest.fixture
def security_client():
    """Test authorization without inheriting test-only auth overrides."""
    dependencies = (require_admin, get_current_user)
    previous_overrides = {
        dependency: app.dependency_overrides[dependency]
        for dependency in dependencies
        if dependency in app.dependency_overrides
    }

    for dependency in dependencies:
        app.dependency_overrides.pop(dependency, None)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        for dependency in dependencies:
            app.dependency_overrides.pop(dependency, None)

        app.dependency_overrides.update(previous_overrides)


def test_evaluation_history_rejects_unauthenticated_request(
    security_client,
):
    response = security_client.get("/api/v1/evaluations/history")

    assert response.status_code == 401


def test_evaluation_history_rejects_non_admin_user(
    security_client,
):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="user")

    response = security_client.get("/api/v1/evaluations/history")

    assert response.status_code == 403


def test_evaluation_history_allows_admin_user(
    security_client,
):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="admin")

    response = security_client.get("/api/v1/evaluations/history")

    assert response.status_code == 200
