from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.auth.dependencies import get_current_user
from app.main import app
from app.repositories.dependencies import get_document_repository


@pytest.fixture
def document_list_client(client):
    user = SimpleNamespace(id=101)
    repository = MagicMock()

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_document_repository] = lambda: repository

    try:
        yield client, user, repository
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_document_repository, None)


def make_document(
    *,
    document_id="doc-1",
    filename="report.pdf",
    status="indexed",
    chunk_count=4,
):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=document_id,
        filename=filename,
        stored_filename=f"{document_id}_report.pdf",
        status=status,
        chunk_count=chunk_count,
        error_message="internal error detail",
        created_at=now,
        updated_at=now,
    )


def test_list_documents_returns_user_documents_and_safe_fields(
    document_list_client,
):
    client, user, repository = document_list_client
    repository.list_by_owner.return_value = [
        make_document(document_id="owned-doc", filename="owned.pdf")
    ]

    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    repository.list_by_owner.assert_called_once_with(user.id)

    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == "owned-doc"
    assert payload[0]["filename"] == "owned.pdf"
    assert payload[0]["status"] == "indexed"
    assert payload[0]["chunk_count"] == 4

    assert "owner_id" not in payload[0]
    assert "stored_filename" not in payload[0]
    assert "error_message" not in payload[0]


def test_list_documents_returns_empty_list_when_user_has_no_documents(
    document_list_client,
):
    client, user, repository = document_list_client
    repository.list_by_owner.return_value = []

    response = client.get("/api/v1/documents")

    assert response.status_code == 200
    assert response.json() == []
    repository.list_by_owner.assert_called_once_with(user.id)

