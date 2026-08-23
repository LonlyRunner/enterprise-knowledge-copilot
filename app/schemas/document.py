import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(
    BaseModel
):
    id: uuid.UUID

    knowledge_base_id: uuid.UUID

    name: str

    file_type: str

    status: str

    source_path: str | None

    task_id: str | None

    error_message: str | None

    retry_count: int

    processing_started_at: (
        datetime | None
    )

    completed_at: (
        datetime | None
    )

    created_at: datetime

    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]


class DocumentUploadResponse(
    BaseModel
):
    document: DocumentResponse

    task_id: str


class DocumentReindexResponse(
    BaseModel
):
    document_id: uuid.UUID

    status: str

    task_id: str