import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.document import (
    DocumentModel,
)
from app.core.config import get_settings
from datetime import datetime, timezone

class DocumentRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
            self,
            *,
            knowledge_base_id: uuid.UUID,
            name: str,
            file_type: str,
            source_path: str | None,
            status: str = "pending",
            document_id: uuid.UUID | None = None,
            tenant_id: str | None = None,
    ) -> DocumentModel:
        tenant_id = tenant_id or get_settings().default_tenant_id
        document = DocumentModel(
            id=document_id or uuid.uuid4(),
            knowledge_base_id=knowledge_base_id,
            name=name,
            file_type=file_type,
            source_path=source_path,
            status=status,
            tenant_id=tenant_id,
        )

        self.session.add(
            document
        )

        await self.session.flush()

        return document


    async def get_by_id(
        self,
        document_id: uuid.UUID,
    ) -> DocumentModel | None:

        statement = (
            select(
                DocumentModel
            )
            .where(
                DocumentModel.id
                == document_id
            )
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        return result.scalar_one_or_none()

    async def list_all(
        self,
    ) -> list[DocumentModel]:

        statement = (
            select(
                DocumentModel
            )
            .order_by(
                DocumentModel.created_at.desc()
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

    async def update_status(
        self,
        document: DocumentModel,
        status: str,
    ) -> DocumentModel:

        document.status = status

        await self.session.flush()

        return document

    async def list_by_knowledge_base(
            self,
            knowledge_base_id: uuid.UUID,
    ) -> list[DocumentModel]:
        statement = (
            select(DocumentModel)
            .where(
                DocumentModel.knowledge_base_id
                == knowledge_base_id
            )
            .order_by(
                DocumentModel.created_at.desc()
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
            document: DocumentModel,
    ) -> None:
        await self.session.delete(
            document
        )

        await self.session.flush()

    async def get_by_id_and_knowledge_base(
            self,
            *,
            document_id: uuid.UUID,
            knowledge_base_id: uuid.UUID,
    ) -> DocumentModel | None:
        statement = (
            select(DocumentModel)
            .where(
                DocumentModel.id
                == document_id,

                DocumentModel.knowledge_base_id
                == knowledge_base_id,
            )
        )

        result = await self.session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def mark_pending(
            self,
            document: DocumentModel,
            *,
            task_id: str | None = None,
    ) -> None:
        document.status = "pending"

        document.task_id = task_id

        document.error_message = None

        document.retry_count = 0

        document.processing_started_at = None

        document.completed_at = None

        await self.session.flush()

    async def mark_processing(
            self,
            document: DocumentModel,
            *,
            retry_count: int = 0,
    ) -> None:
        document.status = "processing"

        document.retry_count = retry_count

        document.error_message = None

        document.processing_started_at = (
            datetime.now(
                timezone.utc
            )
        )

        document.completed_at = None

        await self.session.flush()

    async def mark_completed(
            self,
            document: DocumentModel,
    ) -> None:
        document.status = "completed"

        document.error_message = None

        document.completed_at = (
            datetime.now(
                timezone.utc
            )
        )

        await self.session.flush()

    async def mark_retrying(
            self,
            document: DocumentModel,
            *,
            retry_count: int,
            error_message: str,
    ) -> None:
        document.status = "pending"

        document.retry_count = retry_count

        document.error_message = (
            error_message[:2000]
        )

        await self.session.flush()

    async def mark_failed(
            self,
            document: DocumentModel,
            *,
            retry_count: int,
            error_message: str,
    ) -> None:
        document.status = "failed"

        document.retry_count = retry_count

        document.error_message = (
            error_message[:2000]
        )

        document.completed_at = (
            datetime.now(
                timezone.utc
            )
        )

        await self.session.flush()

    async def get_by_id_for_update(
            self,
            document_id: uuid.UUID,
    ) -> DocumentModel | None:
        statement = (
            select(
                DocumentModel
            )
            .where(
                DocumentModel.id
                == document_id
            )
            .with_for_update()
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id_and_knowledge_base_for_update(
            self,
            *,
            document_id: uuid.UUID,
            knowledge_base_id: uuid.UUID,
    ) -> DocumentModel | None:
        statement = (
            select(
                DocumentModel
            )
            .where(
                DocumentModel.id
                == document_id,

                DocumentModel.knowledge_base_id
                == knowledge_base_id,
            )
            .with_for_update()
        )

        result = (
            await self.session.execute(
                statement
            )
        )

        return result.scalar_one_or_none()
