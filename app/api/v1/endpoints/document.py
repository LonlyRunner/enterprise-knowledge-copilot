import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import require_permission
from app.db.dependencies import get_db
from app.schemas.document import DocumentListResponse, DocumentReindexResponse, DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/knowledge-bases/{knowledge_base_id}/documents", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(knowledge_base_id: uuid.UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("knowledge:write"))):
    document, task_id = await DocumentService(db).upload(knowledge_base_id=knowledge_base_id, file=file, tenant_id=user.tenant_id)
    return {"document": document, "task_id": task_id}


@router.get("/knowledge-bases/{knowledge_base_id}/documents", response_model=DocumentListResponse)
async def list_documents(knowledge_base_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("knowledge:read"))):
    return {"items": await DocumentService(db).list_documents(knowledge_base_id, tenant_id=user.tenant_id)}


@router.get("/knowledge-bases/{knowledge_base_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_document(knowledge_base_id: uuid.UUID, document_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("knowledge:read"))):
    return await DocumentService(db).get_document(knowledge_base_id=knowledge_base_id, document_id=document_id, tenant_id=user.tenant_id)


@router.post("/knowledge-bases/{knowledge_base_id}/documents/{document_id}/reindex", response_model=DocumentReindexResponse)
async def reindex_document(knowledge_base_id: uuid.UUID, document_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("knowledge:write"))):
    task_id = await DocumentService(db).reindex(knowledge_base_id=knowledge_base_id, document_id=document_id, tenant_id=user.tenant_id)
    return {"document_id": document_id, "status": "pending", "task_id": task_id}


@router.delete("/knowledge-bases/{knowledge_base_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(knowledge_base_id: uuid.UUID, document_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("knowledge:write"))):
    await DocumentService(db).delete_document(knowledge_base_id=knowledge_base_id, document_id=document_id, tenant_id=user.tenant_id)
