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
    db_pool_timeout_seconds: float = 30.0
    db_pool_recycle_seconds: int = 1800
    db_pool_use_lifo: bool = True
    db_command_timeout_seconds: float = 60.0
    http_max_connections: int = 100
    http_max_keepalive_connections: int = 20
    http_keepalive_expiry_seconds: float = 30.0
    retry_max_attempts: int = 3
    retry_base_delay_seconds: float = 0.5
    llm_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    embedding_api_key: str = ""
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1024
    embedding_timeout: float = 60.0
    llm_temperature: float = 0.7
    llm_timeout: float = 60.0
    stream_keepalive_seconds: int = 15
    embedding_batch_size: int = 32
    embedding_max_concurrency: int = 2
    diagnostics_enabled: bool = True
    gateway_rate_limit_per_minute: int = 60
    gateway_audit_ttl_seconds: int = 604800
    gateway_default_mode: str = "auto"
    # Deterministic local routing; production can override this with a real
    # provider model such as deepseek-chat.
    gateway_default_model: str = "project-c-router"
    mcp_server_url: str = "http://127.0.0.1:8001/mcp"
    mcp_external_enabled: bool = False
    mcp_auth_token: str = ""
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8001
    document_storage_path: str = "storage/documents"
    max_upload_size_mb: int = 20
    celery_broker_url: str = "redis://127.0.0.1:6379/0"
    celery_result_backend: str = "redis://127.0.0.1:6379/1"
    redis_lock_url: str = "redis://127.0.0.1:6379/2"
    redis_cache_url: str = "redis://127.0.0.1:6379/3"
    redis_url: str = (
        "redis://localhost:6379/0"
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
