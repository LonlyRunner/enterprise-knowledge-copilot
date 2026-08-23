import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.schemas.document import (
    DocumentListResponse,
    DocumentReindexResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.services.document_service import (
    DocumentService,
)


router = APIRouter()


@router.post(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def upload_document(
    knowledge_base_id: uuid.UUID,

    file: UploadFile = File(...),

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = DocumentService(
        db
    )

    document, task_id = (
        await service.upload(
            knowledge_base_id=(
                knowledge_base_id
            ),
            file=file,
        )
    )

    return {
        "document": document,
        "task_id": task_id,
    }


@router.get(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentListResponse,
)
async def list_documents(
    knowledge_base_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = DocumentService(
        db
    )

    items = await service.list_documents(
        knowledge_base_id
    )

    return {
        "items": items
    }


@router.get(
    "/knowledge-bases/{knowledge_base_id}/documents/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    knowledge_base_id: uuid.UUID,
    document_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = DocumentService(
        db
    )

    return await service.get_document(
        knowledge_base_id=(
            knowledge_base_id
        ),
        document_id=document_id,
    )


@router.post(
    "/knowledge-bases/{knowledge_base_id}/documents/{document_id}/reindex",
    response_model=DocumentReindexResponse,
)
async def reindex_document(
    knowledge_base_id: uuid.UUID,
    document_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = DocumentService(
        db
    )

    task_id = await service.reindex(
        knowledge_base_id=(
            knowledge_base_id
        ),
        document_id=document_id,
    )

    return {
        "document_id": (
            document_id
        ),
        "status": "pending",
        "task_id": task_id,
    }


@router.delete(
    "/knowledge-bases/{knowledge_base_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    knowledge_base_id: uuid.UUID,
    document_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
):

    service = DocumentService(
        db
    )

    await service.delete_document(
        knowledge_base_id=(
            knowledge_base_id
        ),
        document_id=document_id,
    )