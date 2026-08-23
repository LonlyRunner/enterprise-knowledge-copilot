import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.conversation import (
    ConversationModel,
)


class ConversationRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        title: str | None = None,
    ) -> ConversationModel:

        conversation = (
            ConversationModel(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                title=title,
            )
        )

        self.session.add(
            conversation
        )

        await self.session.flush()

        return conversation

    async def get_by_id(
        self,
        conversation_id: uuid.UUID,
    ) -> ConversationModel | None:

        statement = (
            select(
                ConversationModel
            )
            .where(
                ConversationModel.id
                == conversation_id
            )
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_by_id_and_knowledge_base(
        self,
        *,
        conversation_id: uuid.UUID,
        knowledge_base_id: uuid.UUID,
    ) -> ConversationModel | None:

        statement = (
            select(
                ConversationModel
            )
            .where(
                ConversationModel.id
                == conversation_id,

                ConversationModel.knowledge_base_id
                == knowledge_base_id,
            )
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def list_by_knowledge_base(
        self,
        knowledge_base_id: uuid.UUID,
    ) -> list[ConversationModel]:

        statement = (
            select(
                ConversationModel
            )
            .where(
                ConversationModel.knowledge_base_id
                == knowledge_base_id
            )
            .order_by(
                ConversationModel.updated_at.desc()
            )
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        return list(
            result.scalars().all()
        )

    async def delete(
        self,
        conversation: ConversationModel,
    ) -> None:

        await self.session.delete(
            conversation
        )

        await self.session.flush()

    async def update_summary(
            self,
            *,
            conversation: ConversationModel,
            summary: str,
            summary_message_id: uuid.UUID,
    ) -> ConversationModel:
        conversation.summary = (
            summary
        )

        conversation.summary_message_id = (
            summary_message_id
        )

        await self.session.flush()

        await self.session.refresh(
            conversation
        )

        return conversation