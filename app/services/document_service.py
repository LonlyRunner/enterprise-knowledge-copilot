import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.repositories.document import (
    DocumentRepository,
)
from app.repositories.knowledge_base import (
    KnowledgeBaseRepository,
)
from app.schemas.document import (
    DocumentResponse,
)

from app.tasks.document_tasks import (
    index_document_task,
)


ALLOWED_FILE_TYPES = {
    ".txt",
    ".md",
    ".markdown",
    ".docx",
    ".pdf",
}


class DocumentService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.settings = get_settings()

        self.document_repository = (
            DocumentRepository(
                session
            )
        )

        self.knowledge_base_repository = (
            KnowledgeBaseRepository(
                session
            )
        )


    async def upload(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        file: UploadFile,
    ) -> tuple[
        DocumentResponse,
        str,
    ]:

        knowledge_base = (
            await self.knowledge_base_repository
            .get_by_id(
                knowledge_base_id
            )
        )

        if knowledge_base is None:
            raise ValueError(
                "Knowledge base not found"
            )

        if not file.filename:
            raise ValueError(
                "Filename is empty"
            )

        original_name = Path(
            file.filename
        ).name

        suffix = Path(
            original_name
        ).suffix.lower()

        if suffix not in ALLOWED_FILE_TYPES:
            raise ValueError(
                f"Unsupported file type: {suffix}"
            )

        document_id = uuid.uuid4()

        storage_directory = (
            Path(
                self.settings.document_storage_path
            )
            / str(
                knowledge_base_id
            )
        )

        storage_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        stored_filename = (
            f"{document_id}{suffix}"
        )

        destination = (
            storage_directory
            / stored_filename
        )

        await self._save_upload(
            file=file,
            destination=destination,
        )

        try:

            document = (
                await self.document_repository.create(
                    document_id=document_id,
                    knowledge_base_id=(
                        knowledge_base_id
                    ),
                    name=original_name,
                    file_type=(
                        suffix.lstrip(".")
                    ),
                    source_path=str(
                        destination
                    ),
                    status="pending",
                )
            )

            task_id = str(
                uuid.uuid4()
            )

            await self.document_repository.mark_pending(
                document,
                task_id=task_id,
            )

            await self.session.commit()

            try:

                index_document_task.apply_async(
                    args=[
                        str(
                            document.id
                        )
                    ],
                    task_id=task_id,
                )

            except Exception as exc:

                document = (
                    await self.document_repository.get_by_id(
                        document.id
                    )
                )

                if document is not None:
                    await self.document_repository.mark_failed(
                        document,
                        retry_count=0,
                        error_message=(
                            f"Failed to enqueue task: {exc}"
                        ),
                    )

                    await self.session.commit()

                raise

            await self.session.refresh(
                document
            )

            return (
                self._to_response(
                    document
                ),
                task_id,
            )

        except Exception:

            await self.session.rollback()

            if destination.exists():
                destination.unlink()

            raise

    async def list_documents(
        self,
        knowledge_base_id: uuid.UUID,
    ) -> list[DocumentResponse]:

        models = (
            await self.document_repository
            .list_by_knowledge_base(
                knowledge_base_id
            )
        )

        return [
            self._to_response(
                model
            )
            for model in models
        ]

    async def get_document(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        document_id: uuid.UUID,
    ) -> DocumentResponse:

        model = (
            await self.document_repository
            .get_by_id_and_knowledge_base(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                document_id=(
                    document_id
                ),
            )
        )

        if model is None:
            raise ValueError(
                "Document not found"
            )

        return self._to_response(
            model
        )

    async def reindex(
            self,
            *,
            knowledge_base_id: uuid.UUID,
            document_id: uuid.UUID,
    ) -> str:

        #
        # SELECT ... FOR UPDATE
        #
        document = (
            await self.document_repository
            .get_by_id_and_knowledge_base_for_update(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                document_id=(
                    document_id
                ),
            )
        )

        if document is None:
            raise ValueError(
                "Document not found"
            )

        #
        # 由于这一行已经锁住，
        # 这里的状态判断现在具备并发意义。
        #
        if document.status in {
            "pending",
            "processing",
        }:
            raise ValueError(
                "Document indexing is already in progress"
            )

        task_id = str(
            uuid.uuid4()
        )

        await self.document_repository.mark_pending(
            document,
            task_id=task_id,
        )

        #
        # COMMIT 后释放 PostgreSQL Row Lock
        #
        await self.session.commit()

        try:

            index_document_task.apply_async(
                args=[
                    str(
                        document.id
                    )
                ],
                task_id=task_id,
            )

        except Exception as exc:

            document = (
                await self.document_repository.get_by_id(
                    document.id
                )
            )

            if document is not None:
                await self.document_repository.mark_failed(
                    document,
                    retry_count=0,
                    error_message=(
                        f"Failed to enqueue task: {exc}"
                    ),
                )

                await self.session.commit()

            raise

        return task_id

    async def delete_document(
        self,
        *,
        knowledge_base_id: uuid.UUID,
        document_id: uuid.UUID,
    ) -> None:

        document = (
            await self.document_repository
            .get_by_id_and_knowledge_base(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                document_id=(
                    document_id
                ),
            )
        )

        if document is None:
            raise ValueError(
                "Document not found"
            )

        source_path = (
            document.source_path
        )

        await self.document_repository.delete(
            document
        )

        await self.session.commit()

        if source_path:
            storage_root = Path(
                self.settings.document_storage_path
            ).resolve()
            path = Path(source_path).resolve()
            if path.is_relative_to(storage_root) and path.is_file():
                path.unlink()

    async def _save_upload(
        self,
        *,
        file: UploadFile,
        destination: Path,
    ) -> None:

        max_bytes = (
            self.settings.max_upload_size_mb
            * 1024
            * 1024
        )

        total_size = 0

        try:

            async with aiofiles.open(
                destination,
                "wb",
            ) as output:

                while True:

                    chunk = await file.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    total_size += len(
                        chunk
                    )

                    if total_size > max_bytes:
                        raise ValueError(
                            "Uploaded file is too large"
                        )

                    await output.write(
                        chunk
                    )

        except Exception:

            if destination.exists():
                destination.unlink()

            raise

        finally:

            await file.close()

    @staticmethod
    def _to_response(
            model,
    ) -> DocumentResponse:

        return DocumentResponse(
            id=model.id,

            knowledge_base_id=(
                model.knowledge_base_id
            ),

            name=model.name,

            file_type=model.file_type,

            status=model.status,

            source_path=model.source_path,

            task_id=model.task_id,

            error_message=(
                model.error_message
            ),

            retry_count=(
                model.retry_count
            ),

            processing_started_at=(
                model.processing_started_at
            ),

            completed_at=(
                model.completed_at
            ),

            created_at=model.created_at,

            updated_at=model.updated_at,
        )
