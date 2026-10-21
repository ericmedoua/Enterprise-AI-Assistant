import logging
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import SessionLocal, get_db
from app.documents.services.file_utils import sanitize_filename
from app.documents.services.file_validator import FileValidator
from app.documents.services.indexing_service import IndexingService
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.dependencies import get_document_repository
from app.schemas.document import DocumentResponse

logger = logging.getLogger(__name__)

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
) -> int | None:
    """Index a document and persist its final registry status."""
    try:
        chunk_count = IndexingService().index_document(
            file_path,
            owner_id=owner_id,
            document_id=document_id,
            source_name=source_name,
        )

        with SessionLocal() as db:
            DocumentRepository(db).update_status(
                document_id,
                "indexed",
                chunk_count=chunk_count,
            )

        return chunk_count

    except Exception:
        logger.exception(
            "Document indexing failed for document_id=%s",
            document_id,
        )

        try:
            with SessionLocal() as db:
                DocumentRepository(db).update_status(
                    document_id,
                    "failed",
                    error_message="Document indexing failed.",
                )
        except Exception:
            logger.exception(
                "Could not persist failed status for document_id=%s",
                document_id,
            )

        return None


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

        DocumentRepository(db).create_document(
            document_id=document_id,
            owner_id=current_user.id,
            filename=filename,
            stored_filename=stored_filename,
        )
    except Exception:
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            logger.exception(
                "Could not clean up uploaded file after failure: %s",
                file_path,
            )
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


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    current_user: User = Depends(get_current_user),
    repository: DocumentRepository = Depends(get_document_repository),
):
    return repository.list_by_owner(current_user.id)
