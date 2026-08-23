import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.message import (
    MessageModel,
)


class MessageRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        *,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
    ) -> MessageModel:

        message = MessageModel(
            conversation_id=(
                conversation_id
            ),
            role=role,
            content=content,
        )

        self.session.add(
            message
        )

        await self.session.flush()

        return message

    async def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
    ) -> list[MessageModel]:

        statement = (
            select(
                MessageModel
            )
            .where(
                MessageModel.conversation_id
                == conversation_id
            )
            .order_by(
                MessageModel.created_at.asc(),
                MessageModel.id.asc(),
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

    async def list_recent(
        self,
        *,
        conversation_id: uuid.UUID,
        limit: int = 10,
    ) -> list[MessageModel]:

        statement = (
            select(
                MessageModel
            )
            .where(
                MessageModel.conversation_id
                == conversation_id
            )
            .order_by(
                MessageModel.created_at.desc(),
                MessageModel.id.desc(),
            )
            .limit(limit)
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        messages = list(
            result.scalars().all()
        )

        #
        # SQL 查出来是：
        # newest → oldest
        #
        # LLM 需要：
        # oldest → newest
        #
        messages.reverse()

        return messages