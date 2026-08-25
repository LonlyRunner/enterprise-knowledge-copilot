from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


settings = get_settings()


engine = create_async_engine(
    settings.database_url,

    echo=settings.db_echo,

    pool_size=settings.db_pool_size,

    max_overflow=settings.db_max_overflow,

    pool_timeout=settings.db_pool_timeout_seconds,

    pool_recycle=settings.db_pool_recycle_seconds,

    pool_use_lifo=settings.db_pool_use_lifo,

    pool_pre_ping=True,

    connect_args={
        "command_timeout": settings.db_command_timeout_seconds,
        "server_settings": {"application_name": settings.app_name},
    },
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,

    class_=AsyncSession,

    expire_on_commit=False,

    autoflush=False,
)
