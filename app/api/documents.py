import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.documents.services.indexing_service import IndexingService
from app.documents.services.file_validator import FileValidator
from app.documents.services.file_utils import sanitize_filename

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIRECTORY = Path("storage")


def _index_document_to_chroma(
    file_path: str,
    *,
    owner_id: str | int,
    document_id: str,
    source_name: str,
) -> int:
    """Index a document with ownership and source metadata."""
    return IndexingService().index_document(
        file_path,
        owner_id=owner_id,
        document_id=document_id,
        source_name=source_name,
    )


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    await FileValidator().validate(file)

    filename = sanitize_filename(file.filename or "upload")
    document_id = str(uuid4())
    stored_filename = f"{document_id}_{filename}"
    file_path = UPLOAD_DIRECTORY / stored_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError:
        raise

    background_tasks.add_task(
        _index_document_to_chroma,
        str(file_path),
        owner_id=current_user.id,
        document_id=document_id,
        source_name=filename,
    )

    return {
        "message": "Document uploaded successfully.",
        "status": "indexing",
        "filename": filename,
        "document_id": document_id,
    }
