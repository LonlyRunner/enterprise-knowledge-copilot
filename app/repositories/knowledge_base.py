import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import (
    KnowledgeBaseModel,
)


class KnowledgeBaseRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> KnowledgeBaseModel:

        model = KnowledgeBaseModel(
            name=name,
            description=description,
        )

        self.session.add(model)

        await self.session.flush()

        return model

    async def get_by_id(
        self,
        knowledge_base_id: uuid.UUID,
    ) -> KnowledgeBaseModel | None:

        statement = (
            select(KnowledgeBaseModel)
            .where(
                KnowledgeBaseModel.id
                == knowledge_base_id
            )
        )

        result = await self.session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_all(
        self,
    ) -> list[KnowledgeBaseModel]:

        statement = (
            select(KnowledgeBaseModel)
            .order_by(
                KnowledgeBaseModel.created_at.desc()
            )
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def delete(
        self,
        model: KnowledgeBaseModel,
    ) -> None:

        await self.session.delete(model)

        await self.session.flush()