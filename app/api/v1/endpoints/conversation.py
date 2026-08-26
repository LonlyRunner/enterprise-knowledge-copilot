import uuid

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.dependencies import (
    get_db,
)
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
)
from app.services.conversation_service import (
    ConversationService,
)
from app.auth.models import User
from app.auth.rbac import require_permission


router = APIRouter()


@router.post(
    "/knowledge-bases/{knowledge_base_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    knowledge_base_id: uuid.UUID,

    request: ConversationCreateRequest,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("chat:use")),
):

    service = (
        ConversationService(
            db
        )
    )

    return await service.create(
        knowledge_base_id=(
            knowledge_base_id
        ),
        title=request.title,
        tenant_id=user.tenant_id,
    )


@router.get(
    "/knowledge-bases/{knowledge_base_id}/conversations",
    response_model=ConversationListResponse,
)
async def list_conversations(
    knowledge_base_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("chat:use")),
):

    service = (
        ConversationService(
            db
        )
    )

    items = await service.list_all(
        knowledge_base_id=(
            knowledge_base_id
        ),
        tenant_id=user.tenant_id,
    )

    return {
        "items": items
    }


@router.get(
    "/knowledge-bases/{knowledge_base_id}/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
async def get_conversation(
    knowledge_base_id: uuid.UUID,
    conversation_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("chat:use")),
):

    service = (
        ConversationService(
            db
        )
    )

    return await service.get_detail(
        knowledge_base_id=(
            knowledge_base_id
        ),
        conversation_id=(
            conversation_id
        ),
        tenant_id=user.tenant_id,
    )


@router.delete(
    "/knowledge-bases/{knowledge_base_id}/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    knowledge_base_id: uuid.UUID,
    conversation_id: uuid.UUID,

    db: AsyncSession = Depends(
        get_db
    ),
    user: User = Depends(require_permission("chat:use")),
):

    service = (
        ConversationService(
            db
        )
    )

    await service.delete(
        knowledge_base_id=(
            knowledge_base_id
        ),
        conversation_id=(
            conversation_id
        ),
        tenant_id=user.tenant_id,
    )
