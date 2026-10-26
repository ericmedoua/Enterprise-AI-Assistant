from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


from app.ai.retrieval.dependencies import get_chroma_service
from app.api import documents as documents_api
from app.auth.dependencies import get_current_user
from app.main import app
from app.repositories.dependencies import get_document_repository


@pytest.fixture
def document_delete_client(client, monkeypatch, tmp_path):
    user = SimpleNamespace(id=101)
    repository = MagicMock()
    chroma_service = MagicMock()
    storage = tmp_path / "storage"
    storage.mkdir()

    monkeypatch.setattr(documents_api, "UPLOAD_DIRECTORY", storage)

    previous_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_document_repository] = lambda: repository
    app.dependency_overrides[get_chroma_service] = lambda: chroma_service

    try:
        yield client, user, repository, chroma_service, storage
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def make_document(
    *, owner_id=101, status="indexed", stored_filename="doc-1_report.pdf"
):
    return SimpleNamespace(
        id="doc-1",
        owner_id=owner_id,
        status=status,
        stored_filename=stored_filename,
    )


def test_delete_document_removes_vectors_file_and_record(document_delete_client):
    client, user, repository, chroma_service, storage = document_delete_client
    document = make_document()
    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")
    repository.get_owned_document.return_value = document
    repository.begin_deletion.return_value = document
    repository.delete_owned_document.return_value = True

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 200
    assert response.json()["document_id"] == "doc-1"
    assert not file_path.exists()
    chroma_service.delete_document.assert_called_once_with(
        owner_id=user.id,
        document_id="doc-1",
    )
    repository.begin_deletion.assert_called_once_with("doc-1", user.id)
    repository.delete_owned_document.assert_called_once_with("doc-1", user.id)


def test_delete_document_returns_404_when_document_is_not_found(
    document_delete_client,
):
    client, user, repository, chroma_service, storage = document_delete_client
    repository.get_owned_document.return_value = None

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 404
    repository.begin_deletion.assert_not_called()
    chroma_service.delete_document.assert_not_called()
    repository.delete_owned_document.assert_not_called()
    assert list(storage.iterdir()) == []

    response = client.delete("/api/v1/documents/doc-1")


def test_delete_document_rejects_indexing_status_without_cleanup(
    document_delete_client,
):
    client, user, repository, chroma_service, storage = document_delete_client
    repository.get_owned_document.return_value = make_document(status="indexing")

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 409
    repository.begin_deletion.assert_not_called()
    chroma_service.delete_document.assert_not_called()
    repository.delete_owned_document.assert_not_called()
    assert list(storage.iterdir()) == []


def test_delete_document_keeps_file_and_record_if_chroma_fails(
    document_delete_client,
):
    client, user, repository, chroma_service, storage = document_delete_client
    document = make_document()
    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")
    repository.get_owned_document.return_value = document
    repository.begin_deletion.return_value = document
    chroma_service.delete_document.side_effect = RuntimeError("Chroma unavailable")

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 500
    assert file_path.exists()
    repository.begin_deletion.assert_called_once_with("doc-1", user.id)
    repository.delete_owned_document.assert_not_called()


def test_delete_document_keeps_record_if_file_removal_fails(
    document_delete_client,
    monkeypatch,
):
    client, user, repository, chroma_service, storage = document_delete_client
    document = make_document()
    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")
    repository.get_owned_document.return_value = document
    repository.begin_deletion.return_value = document

    def fail_unlink(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(type(file_path), "unlink", fail_unlink)

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 500
    repository.begin_deletion.assert_called_once_with("doc-1", user.id)
    chroma_service.delete_document.assert_called_once()
    repository.delete_owned_document.assert_not_called()


def test_delete_document_rejects_unsafe_storage_path_without_cleanup(
    document_delete_client,
):
    client, user, repository, chroma_service, storage = document_delete_client
    repository.get_owned_document.return_value = make_document(
        stored_filename="../outside.txt"
    )

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 500
    repository.begin_deletion.assert_not_called()
    chroma_service.delete_document.assert_not_called()
    repository.delete_owned_document.assert_not_called()
    assert list(storage.iterdir()) == []


def test_delete_document_returns_500_if_registry_delete_fails(
    document_delete_client,
):
    client, user, repository, chroma_service, storage = document_delete_client
    document = make_document()
    file_path = storage / document.stored_filename
    file_path.write_text("test document", encoding="utf-8")
    repository.get_owned_document.return_value = document
    repository.begin_deletion.return_value = document
    repository.delete_owned_document.side_effect = RuntimeError("database unavailable")

    response = client.delete("/api/v1/documents/doc-1")

    assert response.status_code == 500
    assert not file_path.exists()
    repository.begin_deletion.assert_called_once_with("doc-1", user.id)
    chroma_service.delete_document.assert_called_once()
