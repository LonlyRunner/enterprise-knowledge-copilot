import uuid

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.repositories.conversation import (
    ConversationRepository,
)
from app.repositories.knowledge_base import (
    KnowledgeBaseRepository,
)
from app.repositories.message import (
    MessageRepository,
)
from app.schemas.conversation import (
    ConversationResponse,
    MessageResponse,
)


class ConversationService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.conversation_repository = (
            ConversationRepository(
                session
            )
        )

        self.message_repository = (
            MessageRepository(
                session
            )
        )

        self.knowledge_base_repository = (
            KnowledgeBaseRepository(
                session
            )
        )

    async def create(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        title: str | None = None,
        tenant_id: str | None = None,
    ) -> ConversationResponse:

        knowledge_base = (
            await self
            .knowledge_base_repository
            .get_by_id(
                knowledge_base_id, tenant_id=tenant_id
            )
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge base not found"
            )

        conversation = (
            await self
            .conversation_repository
            .create(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                title=title,
            )
        )

        await self.session.commit()

        await self.session.refresh(
            conversation
        )

        return self._to_response(
            conversation
        )

    async def list_all(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        tenant_id: str | None = None,
    ) -> list[ConversationResponse]:

        if await self.knowledge_base_repository.get_by_id(knowledge_base_id, tenant_id=tenant_id) is None:
            raise ValueError("Knowledge base not found")
        conversations = (
            await self
            .conversation_repository
            .list_by_knowledge_base(
                knowledge_base_id
            )
        )

        return [
            self._to_response(
                conversation
            )
            for conversation
            in conversations
        ]

    async def get_detail(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        conversation_id: uuid.UUID,
        tenant_id: str | None = None,
    ):

        if await self.knowledge_base_repository.get_by_id(knowledge_base_id, tenant_id=tenant_id) is None:
            raise ValueError("Knowledge base not found")
        conversation = (
            await self
            .conversation_repository
            .get_by_id_and_knowledge_base(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            raise ValueError(
                "Conversation not found"
            )

        messages = (
            await self
            .message_repository
            .list_by_conversation(
                conversation_id
            )
        )

        return {
            "conversation": (
                self._to_response(
                    conversation
                )
            ),
            "messages": [
                MessageResponse(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=(
                        message.created_at
                    ),
                )
                for message in messages
            ],
        }

    async def delete(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        conversation_id: uuid.UUID,
        tenant_id: str | None = None,
    ) -> None:

        if await self.knowledge_base_repository.get_by_id(knowledge_base_id, tenant_id=tenant_id) is None:
            raise ValueError("Knowledge base not found")
        conversation = (
            await self
            .conversation_repository
            .get_by_id_and_knowledge_base(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                conversation_id=(
                    conversation_id
                ),
            )
        )

        if conversation is None:
            raise ValueError(
                "Conversation not found"
            )

        await self.conversation_repository.delete(
            conversation
        )

        await self.session.commit()

    @staticmethod
    def _to_response(
        conversation,
    ) -> ConversationResponse:

        return ConversationResponse(
            id=conversation.id,

            knowledge_base_id=(
                conversation.knowledge_base_id
            ),

            title=conversation.title,

            created_at=(
                conversation.created_at
            ),

            updated_at=(
                conversation.updated_at
            ),
        )
