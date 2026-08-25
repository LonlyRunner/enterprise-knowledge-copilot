"""Local integration probes for async, pooling, retry, cache and batching."""
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.semantic import SemanticCache
from app.core.config import get_settings
from app.db.dependencies import get_db
from app.db.session import engine
from app.llm.client import create_llm_client
from app.rag.context import TokenBudget, TokenCounter
from app.rag.embedding import EmbeddingClient
from app.utils.sse import encode_sse

router = APIRouter(prefix="/performance", tags=["Performance"])


def _enabled() -> None:
    if not get_settings().diagnostics_enabled:
        raise HTTPException(status_code=404, detail="diagnostics disabled")


class TokenProbeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class EmbeddingProbeRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=128)


class CacheProbeRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(max_length=2_000)


@router.get("/config")
async def performance_config():
    _enabled()
    settings = get_settings()
    return {
        "timeouts": {"llm_seconds": settings.llm_timeout, "embedding_seconds": settings.embedding_timeout},
        "retry": {"max_attempts": settings.retry_max_attempts, "base_delay_seconds": settings.retry_base_delay_seconds},
        "http_pool": {"max_connections": settings.http_max_connections, "max_keepalive": settings.http_max_keepalive_connections},
        "embedding": {"batch_size": settings.embedding_batch_size, "max_concurrency": settings.embedding_max_concurrency},
        "database": {"pool_size": settings.db_pool_size, "max_overflow": settings.db_max_overflow, "pool_timeout_seconds": settings.db_pool_timeout_seconds},
        "token_budget": TokenBudget().as_dict(),
    }


@router.post("/token-estimate")
async def performance_token_estimate(request: TokenProbeRequest):
    _enabled()
    counter = TokenCounter()
    return {"token_count": counter.count_text(request.text), "budget": TokenBudget().as_dict()}


@router.get("/db-pool")
async def performance_db_pool(db: AsyncSession = Depends(get_db)):
    _enabled()
    await db.execute(text("SELECT 1"))
    pool = engine.pool
    return {"ok": True, "pool": pool.status() if hasattr(pool, "status") else str(pool)}


@router.post("/embedding-batch")
async def performance_embedding_batch(request: EmbeddingProbeRequest):
    _enabled()
    client = EmbeddingClient()
    try:
        vectors = await client.embed_batch(request.texts)
        return {"count": len(vectors), "dimensions": len(vectors[0]) if vectors else 0}
    finally:
        await client.close()


@router.post("/cache")
async def performance_cache(request: CacheProbeRequest):
    _enabled()
    cache = SemanticCache(ttl_seconds=120)
    try:
        await cache.set("diagnostic", request.key, 1, {"value": request.value})
        result = await cache.get("diagnostic", request.key, 1)
        return {"hit": result is not None, "value": result.get("value") if result else None}
    finally:
        await cache.close()


@router.post("/stream")
async def performance_stream(request: TokenProbeRequest):
    _enabled()
    llm = create_llm_client()

    async def events() -> AsyncIterator[str]:
        yield encode_sse("start", {})
        try:
            async for delta in llm.stream_chat(request.text):
                yield encode_sse("delta", {"content": delta})
            yield encode_sse("done", {})
        except Exception as exc:
            yield encode_sse("error", {"message": str(exc)})
        finally:
            await llm.close()

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
