from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class DocumentHealthResponse(BaseModel):
    total_documents: int
    indexing_count: int
    indexed_count: int
    failed_count: int
    deleting_count: int
    deletion_due_count: int
    deletion_scheduled_count: int
    total_deletion_attempts: int
    generated_at: datetime
