from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "enterprise-knowledge-copilot"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = (
        "postgresql+asyncpg://"
        "postgres:postgres@127.0.0.1:5432/enterprise_rag"
    )

    db_echo: bool = False

    db_pool_size: int = 10

    db_max_overflow: int = 20

    # LLM
    llm_provider: str = "deepseek"

    deepseek_api_key: str = "sk-5505e9a3a7f84078ad0d4a4361b3eb29"
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

    embedding_api_key: str = "sk-ws-H.EYHLHID.BEYX.MEYCIQDDsf7JkdxDEOoAfCjbW5GVeEzVQUDM0m7Ccov8bq3AqgIhAPDBVUpZQzsswDxdTHU2kaeUap_fImXEu7p2vCipplmB"
    embedding_base_url: str = "https://ws-in1go1ee7kvuywhh.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    embedding_model: str = "qwen3.7-text-embedding"

    embedding_timeout: float = 60.0

    llm_temperature: float = 0.7
    llm_timeout: float = 60.0

    # File Storage
    document_storage_path: str = "storage/documents"

    max_upload_size_mb: int = 20

    # Celery / Redis
    celery_broker_url: str = (
        "redis://127.0.0.1:6379/0"
    )

    celery_result_backend: str = (
        "redis://127.0.0.1:6379/1"
    )

    # Redis Distributed Lock
    redis_lock_url: str = (
        "redis://127.0.0.1:6379/2"
    )

    document_lock_ttl_seconds: int = 300




    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )




@lru_cache
def get_settings() -> Settings:
    return Settings()