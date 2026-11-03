from types import SimpleNamespace

import pytest

from app.main import app
from app.auth.authorization import require_admin
from app.auth.dependencies import get_current_user
from app.repositories.dependencies import get_document_repository


@pytest.fixture
def admin_metrics():
    return {
        "total_documents": 20,
        "indexing_count": 2,
        "indexed_count": 12,
        "failed_count": 1,
        "deleting_count": 5,
        "deletion_due_count": 3,
        "deletion_scheduled_count": 2,
        "total_deletion_attempts": 9,
    }


def test_document_health_endpoint_returns_metrics_for_admin(
    client,
    monkeypatch,
    admin_metrics,
):
    monkeypatch.setitem(
        app.dependency_overrides,
        require_admin,
        lambda: SimpleNamespace(role="admin"),
    )

    repository = SimpleNamespace(get_document_health_metrics=lambda: admin_metrics)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_document_repository,
        lambda: repository,
    )

    response = client.get("/api/v1/admin/document-health")

    assert response.status_code == 200

    data = response.json()

    for key, expected_value in admin_metrics.items():
        assert data[key] == expected_value

    assert "generated_at" in data
    assert data["generated_at"] is not None


def test_document_health_endpoint_rejects_regular_user(
    client,
    monkeypatch,
):
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: SimpleNamespace(role="user"),
    )

    response = client.get("/api/v1/admin/document-health")

    assert response.status_code == 403


def test_document_health_endpoint_does_not_expose_sensitive_fields(
    client,
    monkeypatch,
    admin_metrics,
):
    monkeypatch.setitem(
        app.dependency_overrides,
        require_admin,
        lambda: SimpleNamespace(role="admin"),
    )

    repository = SimpleNamespace(get_document_health_metrics=lambda: admin_metrics)

    monkeypatch.setitem(
        app.dependency_overrides,
        get_document_repository,
        lambda: repository,
    )

    response = client.get("/api/v1/admin/document-health")

    assert response.status_code == 200

    data = response.json()

    assert "filename" not in data
    assert "owner_id" not in data
    assert "error_message" not in data
    assert "stored_filename" not in data
