import uuid

from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.document_chunk import (
    DocumentChunkModel,
)
from app.models.document import (
    DocumentModel,
)
from app.core.config import get_settings

class DocumentChunkRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create_many(
        self,
        *,
        document_id: uuid.UUID,
        chunks: list[dict],
        tenant_id: str | None = None,
    ) -> list[DocumentChunkModel]:
        tenant_id = tenant_id or get_settings().default_tenant_id

        models = [
            DocumentChunkModel(
                document_id=document_id,
                chunk_index=item["chunk_index"],
                content=item["content"],
                embedding=item["embedding"],
                tenant_id=item.get("tenant_id", tenant_id),
            )
            for item in chunks
        ]

        self.session.add_all(models)

        await self.session.flush()

        return models

    async def list_by_document(
        self,
        document_id: uuid.UUID,
    ) -> list[DocumentChunkModel]:

        statement = (
            select(DocumentChunkModel)
            .where(
                DocumentChunkModel.document_id
                == document_id
            )
            .order_by(
                DocumentChunkModel.chunk_index
            )
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def delete_by_document(
        self,
        document_id: uuid.UUID,
    ) -> None:

        statement = (
            delete(DocumentChunkModel)
            .where(
                DocumentChunkModel.document_id
                == document_id
            )
        )

        await self.session.execute(
            statement
        )

    async def list_by_knowledge_base_for_retrieval(
            self,
            tenant_id: str | None,
            knowledge_base_id: uuid.UUID,
    ) -> list[tuple[
        DocumentChunkModel,
        str,
    ]]:
        tenant_id = tenant_id or get_settings().default_tenant_id
        statement = (
            select(
                DocumentChunkModel,
                DocumentModel.name,
            )
            .join(
                DocumentModel,
                DocumentModel.id
                == DocumentChunkModel.document_id,
            )
            .where(DocumentModel.knowledge_base_id == knowledge_base_id,
                   DocumentChunkModel.tenant_id == tenant_id)
            .order_by(
                DocumentChunkModel.created_at.asc(),
                DocumentChunkModel.chunk_index.asc(),
            )
        )

        result = await self.session.execute(
            statement
        )

        return list(
            result.all()
        )
