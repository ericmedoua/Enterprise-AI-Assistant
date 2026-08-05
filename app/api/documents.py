import shutil
from pathlib import Path

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import HTTPException
from fastapi import UploadFile

from app.ai.retrieval.dependencies import get_chroma_service
from app.documents.services.indexing_service import IndexingService

from app.documents.services.file_validator import FileValidator
from app.documents.services.file_utils import sanitize_filename

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIRECTORY = Path("storage")


def _index_document_to_chroma(file_path: str):
    documents = IndexingService().index_document(file_path)
    get_chroma_service().add_documents(documents)


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
):

    UPLOAD_DIRECTORY.mkdir(exist_ok=True)

    await FileValidator().validate(file)

    filename = sanitize_filename(file.filename)

    file_path = UPLOAD_DIRECTORY / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        background_tasks.add_task(
            _index_document_to_chroma,
            str(file_path),
        )

        return {
            "message": "Document uploaded successfully.",
            "status": "indexing",
            "filename": filename,
        }
