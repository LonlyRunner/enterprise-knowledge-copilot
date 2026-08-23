import uuid

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.repositories.knowledge_base import (
    KnowledgeBaseRepository,
)
from app.schemas.knowledge_base import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseResponse,
)


class KnowledgeBaseService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.repository = (
            KnowledgeBaseRepository(
                session
            )
        )

    async def create(
        self,
        request: KnowledgeBaseCreateRequest,
    ) -> KnowledgeBaseResponse:

        model = (
            await self.repository.create(
                name=request.name,
                description=(
                    request.description
                ),
            )
        )

        await self.session.commit()

        return KnowledgeBaseResponse(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
        )

    async def list_all(
        self,
    ) -> list[
        KnowledgeBaseResponse
    ]:

        models = (
            await self.repository.list_all()
        )

        return [
            KnowledgeBaseResponse(
                id=model.id,
                name=model.name,
                description=model.description,
                created_at=model.created_at,
            )
            for model in models
        ]

    async def delete(
        self,
        knowledge_base_id: uuid.UUID,
    ) -> None:

        model = (
            await self.repository.get_by_id(
                knowledge_base_id
            )
        )

        if model is None:
            raise ValueError(
                "Knowledge base not found"
            )

        await self.repository.delete(
            model
        )

        await self.session.commit()