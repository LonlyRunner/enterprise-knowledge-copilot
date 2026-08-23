import asyncio
import uuid

from app.db.worker_session import (
    create_worker_engine,
    create_worker_session_factory,
)
from app.repositories.document import (
    DocumentRepository,
)
from app.services.document_index_service import (
    DocumentIndexService,
)
from app.tasks.exceptions import (
    is_retryable_exception,
)
from app.worker.celery_app import (
    celery_app,
)

from app.core.config import (
    get_settings,
)
from app.infrastructure.redis_lock import (
    RedisDistributedLock,
)
from app.tasks.exceptions import (
    DocumentLockBusyException,
    is_retryable_exception,
)


MAX_RETRIES = 3

settings = get_settings()

async def _run_index(
    *,
    document_id: str,
    retry_count: int,
) -> dict:

    parsed_document_id = (
        uuid.UUID(
            document_id
        )
    )

    lock = RedisDistributedLock(
        redis_url=(
            settings.redis_lock_url
        ),
        key=(
            f"document:index:"
            f"{document_id}"
        ),
        ttl_seconds=(
            settings
            .document_lock_ttl_seconds
        ),
    )

    acquired = (
        await lock.acquire()
    )

    if not acquired:

        await lock.close()

        raise DocumentLockBusyException(
            "Document is already being indexed "
            "by another worker"
        )

    engine = (
        create_worker_engine()
    )

    session_factory = (
        create_worker_session_factory(
            engine
        )
    )

    try:

        async with session_factory() as session:

            service = (
                DocumentIndexService(
                    session
                )
            )

            chunks = (
                await service.index(
                    document_id=(
                        parsed_document_id
                    ),
                    retry_count=(
                        retry_count
                    ),
                )
            )

            return {
                "document_id": (
                    document_id
                ),
                "chunks": chunks,
                "status": "completed",
            }

    finally:

        await engine.dispose()

        try:

            await lock.release()

        finally:

            await lock.close()

async def _mark_retrying(
    *,
    document_id: str,
    retry_count: int,
    error_message: str,
) -> None:

    engine = (
        create_worker_engine()
    )

    session_factory = (
        create_worker_session_factory(
            engine
        )
    )

    try:

        async with session_factory() as session:

            repository = (
                DocumentRepository(
                    session
                )
            )

            document = (
                await repository.get_by_id(
                    uuid.UUID(
                        document_id
                    )
                )
            )

            if document is None:
                return

            await repository.mark_retrying(
                document,
                retry_count=retry_count,
                error_message=error_message,
            )

            await session.commit()

    finally:

        await engine.dispose()


async def _mark_failed(
    *,
    document_id: str,
    retry_count: int,
    error_message: str,
) -> None:

    engine = (
        create_worker_engine()
    )

    session_factory = (
        create_worker_session_factory(
            engine
        )
    )

    try:

        async with session_factory() as session:

            repository = (
                DocumentRepository(
                    session
                )
            )

            document = (
                await repository.get_by_id(
                    uuid.UUID(
                        document_id
                    )
                )
            )

            if document is None:
                return

            await repository.mark_failed(
                document,
                retry_count=retry_count,
                error_message=error_message,
            )

            await session.commit()

    finally:

        await engine.dispose()


@celery_app.task(
    bind=True,
    name="documents.index",
    max_retries=MAX_RETRIES,
)
def index_document_task(
    self,
    document_id: str,
):

    retry_count = (
        self.request.retries
    )

    try:

        return asyncio.run(
            _run_index(
                document_id=(
                    document_id
                ),
                retry_count=(
                    retry_count
                ),
            )
        )

    except Exception as exc:

        error_message = (
            f"{type(exc).__name__}: {exc}"
        )

        should_retry = (
            is_retryable_exception(
                exc
            )
        )

        if (
            should_retry
            and retry_count
            < MAX_RETRIES
        ):

            next_retry_count = (
                retry_count + 1
            )

            if not isinstance(
                    exc,
                    DocumentLockBusyException,
            ):
                asyncio.run(
                    _mark_retrying(
                        document_id=(
                            document_id
                        ),
                        retry_count=(
                            next_retry_count
                        ),
                        error_message=(
                            error_message
                        ),
                    )
                )

            countdown = min(
                2 ** next_retry_count,
                60,
            )

            raise self.retry(
                exc=exc,
                countdown=countdown,
            )

        asyncio.run(
            _mark_failed(
                document_id=document_id,
                retry_count=(
                    retry_count
                ),
                error_message=(
                    error_message
                ),
            )
        )

        raise