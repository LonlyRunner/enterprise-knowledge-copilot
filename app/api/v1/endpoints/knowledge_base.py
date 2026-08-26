import uuid

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.dependencies import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
)
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
)
from app.auth.models import User
from app.auth.rbac import require_permission


router = APIRouter()


@router.post(
    "/knowledge-bases",
    response_model=KnowledgeBaseResponse,
)
async def create_knowledge_base(
    request: KnowledgeBaseCreateRequest,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("knowledge:write")),
):

    service = KnowledgeBaseService(
        db
    )

    return await service.create(request, tenant_id=user.tenant_id)


@router.get(
    "/knowledge-bases",
    response_model=KnowledgeBaseListResponse,
)
async def list_knowledge_bases(
    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("knowledge:read")),
):

    service = KnowledgeBaseService(
        db
    )

    items = await service.list_all(tenant_id=user.tenant_id)

    return {
        "items": items
    }


@router.delete(
    "/knowledge-bases/{knowledge_base_id}",
    status_code=204,
)
async def delete_knowledge_base(
    knowledge_base_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("knowledge:write")),
):

    service = KnowledgeBaseService(
        db
    )

    await service.delete(knowledge_base_id, tenant_id=user.tenant_id)
