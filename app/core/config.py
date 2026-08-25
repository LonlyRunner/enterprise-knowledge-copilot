from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "enterprise-knowledge-copilot"
    app_version: str = "0.1.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/enterprise_rag"
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20
    llm_provider: str = "deepseek"
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    embedding_api_key: str
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1024
    embedding_timeout: float = 60.0
    llm_temperature: float = 0.7
    llm_timeout: float = 60.0
    document_storage_path: str = "storage/documents"
    max_upload_size_mb: int = 20
    celery_broker_url: str = "redis://127.0.0.1:6379/0"
    celery_result_backend: str = "redis://127.0.0.1:6379/1"
    redis_lock_url: str = "redis://127.0.0.1:6379/2"
    redis_cache_url: str = "redis://127.0.0.1:6379/3"
    langgraph_checkpoint_url: str = (
        "redis://127.0.0.1:6379/4"
    )
    document_lock_ttl_seconds: int = 300
    # Empty is allowed for local imports/tests, but authentication must reject it.
    jwt_secret: str = ""
    auth_enabled: bool = False
    access_token_expire_minutes: int = 120
    default_tenant_id: str = "default"
    vector_store_backend: str = "postgres"
    milvus_uri: str = "http://127.0.0.1:19530"
    milvus_collection: str = "enterprise_document_chunks"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
