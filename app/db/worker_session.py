from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


settings = get_settings()


def create_worker_engine():

    return create_async_engine(
        settings.database_url,

        echo=False,

        poolclass=NullPool,
    )


def create_worker_session_factory(
    engine,
):

    return async_sessionmaker(
        bind=engine,

        class_=AsyncSession,

        expire_on_commit=False,

        autoflush=False,
    )