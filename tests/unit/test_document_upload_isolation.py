import asyncio
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import BackgroundTasks, UploadFile

from app.api import documents


def test_same_filename_uploads_get_unique_paths_and_owner_metadata(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(documents, "UPLOAD_DIRECTORY", tmp_path)

    async def accept_file(self, file):
        return None

    monkeypatch.setattr(
        documents.FileValidator,
        "validate",
        accept_file,
    )

    user_a = SimpleNamespace(id=101)
    user_b = SimpleNamespace(id=202)

    async def upload_for(user):
        background_tasks = BackgroundTasks()
        file = UploadFile(
            filename="report.pdf",
            file=BytesIO(b"sample document content"),
        )

        result = await documents.upload_document(
            background_tasks=background_tasks,
            file=file,
            current_user=user,
        )

        return result, background_tasks

    result_a, tasks_a = asyncio.run(upload_for(user_a))
    result_b, tasks_b = asyncio.run(upload_for(user_b))

    path_a = tmp_path / f"{result_a['document_id']}_report.pdf"
    path_b = tmp_path / f"{result_b['document_id']}_report.pdf"

    assert path_a.exists()
    assert path_b.exists()
    assert path_a != path_b
    assert path_a.read_bytes() == b"sample document content"
    assert path_b.read_bytes() == b"sample document content"
    assert result_a["document_id"] != result_b["document_id"]

    task_a = tasks_a.tasks[0]
    task_b = tasks_b.tasks[0]

    assert task_a.func is documents._index_document_to_chroma
    assert task_b.func is documents._index_document_to_chroma

    assert task_a.args == (str(path_a),)
    assert task_b.args == (str(path_b),)

    assert task_a.kwargs == {
        "owner_id": 101,
        "document_id": result_a["document_id"],
        "source_name": "report.pdf",
    }
    assert task_b.kwargs == {
        "owner_id": 202,
        "document_id": result_b["document_id"],
        "source_name": "report.pdf",
    }
