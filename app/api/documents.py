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
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from app.ai.retrieval.dependencies import get_chroma_service

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
    except Exception:
        logger.exception(
            "Document indexing failed for document_id=%s",
            document_id,
        )

        try:
            get_chroma_service().delete_document(
                owner_id=owner_id,
                document_id=document_id,
            )
        except Exception:
            logger.exception(
                "Could not clean up vectors after indexing failure for document_id=%s",
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

    try:
        with SessionLocal() as db:
            DocumentRepository(db).update_status(
                document_id,
                "indexed",
                chunk_count=chunk_count,
            )
    except Exception:
        logger.exception(
            "Document indexing completed, but indexed status could not be saved: "
            "document_id=%s",
            document_id,
        )
        return None

    return chunk_count


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


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    repository: DocumentRepository = Depends(get_document_repository),
    chroma_service=Depends(get_chroma_service),
):
    document = repository.get_owned_document(
        document_id,
        current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if document.status == "indexing":
        raise HTTPException(
            status_code=409,
            detail="Document is still indexing. Try again later.",
        )

    storage_root = UPLOAD_DIRECTORY.resolve()
    file_path = (storage_root / document.stored_filename).resolve()

    if file_path.parent != storage_root or file_path.name != document.stored_filename:
        logger.error(
            "Unsafe document storage path for document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Document storage path is invalid.",
        )

    # Persist deletion intent so a failed cleanup remains recoverable.
    try:
        deleting_document = repository.begin_deletion(
            document_id,
            current_user.id,
        )
    except ValueError as exc:
        logger.warning(
            "Document cannot enter deletion state: document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=409,
            detail="Document cannot be deleted in its current state.",
        ) from exc
    except Exception as exc:
        logger.exception(
            "Could not mark document for deletion: document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Could not start document deletion.",
        ) from exc

    if deleting_document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Claim the committed deleting record. Keep this DB session open through
    # cleanup so the recovery worker cannot claim the same row concurrently.
    try:
        claimed_document = repository.claim_pending_deletion(
            document_id,
            owner_id=current_user.id,
        )
    except Exception as exc:
        logger.exception(
            "Could not claim document deletion: document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Could not start document deletion.",
        ) from exc

    if claimed_document is None:
        raise HTTPException(
            status_code=409,
            detail="Document deletion is already in progress. Retry later.",
        )

    try:
        chroma_service.delete_document(
            owner_id=current_user.id,
            document_id=claimed_document.id,
        )
    except Exception as exc:
        logger.exception(
            "Could not delete document vectors: document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Could not delete document vectors. Retry deletion later.",
        ) from exc

    try:
        file_path.unlink(missing_ok=True)
    except OSError as exc:
        logger.exception(
            "Could not delete stored document file: document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Could not delete stored document file. Retry deletion later.",
        ) from exc

    try:
        deleted = repository.delete_owned_document(
            document_id,
            current_user.id,
        )
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Could not delete document registry record: document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Could not delete document record. Retry deletion later.",
        ) from exc

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }
