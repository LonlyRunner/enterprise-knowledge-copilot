import logging
import shutil
import uuid
from pathlib import Path

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
from app.core.config import get_settings


logger = logging.getLogger(__name__)


class KnowledgeBaseService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.settings = get_settings()

        self.repository = (
            KnowledgeBaseRepository(
                session
            )
        )

    async def create(
        self,
        request: KnowledgeBaseCreateRequest,
        *,
        tenant_id: str | None = None,
    ) -> KnowledgeBaseResponse:

        model = (
            await self.repository.create(
                name=request.name,
                description=(
                    request.description
                ),
                tenant_id=tenant_id or self.settings.default_tenant_id,
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
        *,
        tenant_id: str | None = None,
    ) -> list[
        KnowledgeBaseResponse
    ]:

        models = (
            await self.repository.list_all(tenant_id=tenant_id)
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
        *,
        tenant_id: str | None = None,
    ) -> None:

        model = (
            await self.repository.get_by_id(
                knowledge_base_id,
                tenant_id=tenant_id,
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

        # Uploaded files are stored below one directory per knowledge base.
        # Remove only that exact, validated directory after the DB commit so
        # a filesystem issue cannot roll back a successful database delete.
        storage_root = Path(self.settings.document_storage_path).resolve()
        storage_directory = (storage_root / str(knowledge_base_id)).resolve()
        if storage_directory.parent == storage_root and storage_directory.name == str(knowledge_base_id):
            try:
                if storage_directory.is_symlink():
                    storage_directory.unlink()
                elif storage_directory.is_dir():
                    shutil.rmtree(storage_directory)
            except OSError:
                logger.warning(
                    "Unable to remove knowledge base storage directory %s",
                    storage_directory,
                    exc_info=True,
                )
