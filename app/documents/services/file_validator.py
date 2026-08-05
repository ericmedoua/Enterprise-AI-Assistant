from pathlib import Path

from fastapi import HTTPException
from fastapi import UploadFile

from app.core.upload_constants import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE,
)


class FileValidator:
    async def validate(
        self,
        file: UploadFile,
    ):

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed.",
            )

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid content type.",
            )

        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File exceeds maximum size.",
            )

        await file.seek(0)
