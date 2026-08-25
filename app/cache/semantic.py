"""Redis-backed semantic/result cache used by stateless RAG queries."""
import hashlib
import json
import logging
from functools import lru_cache
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cache_redis() -> Redis:
    """One process-wide async Redis pool instead of one pool per request."""
    settings = get_settings()
    return Redis.from_url(
        settings.redis_cache_url,
        decode_responses=True,
        max_connections=settings.http_max_connections,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )


class SemanticCache:
    def __init__(self, redis: Redis | None = None, ttl_seconds: int = 600):
        self.redis = redis or get_cache_redis()
        self._owned = redis is not None
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def make_key(knowledge_base_id: str, question: str, top_k: int) -> str:
        normalized = " ".join(question.strip().lower().split())
        digest = hashlib.sha256(f"{knowledge_base_id}:{top_k}:{normalized}".encode()).hexdigest()
        return f"rag:query:{knowledge_base_id}:{digest}"

    async def get(self, knowledge_base_id: str, question: str, top_k: int) -> dict[str, Any] | None:
        try:
            value = await self.redis.get(self.make_key(knowledge_base_id, question, top_k))
        except Exception:
            logger.warning("semantic cache read failed", exc_info=True)
            return None
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    async def set(self, knowledge_base_id: str, question: str, top_k: int, value: dict[str, Any]) -> None:
        try:
            await self.redis.set(self.make_key(knowledge_base_id, question, top_k), json.dumps(value, ensure_ascii=False), ex=self.ttl_seconds)
        except Exception:
            logger.warning("semantic cache write failed", exc_info=True)

    async def invalidate_knowledge_base(self, knowledge_base_id: str) -> None:
        try:
            keys = [key async for key in self.redis.scan_iter(match=f"rag:query:{knowledge_base_id}:*")]
            if keys:
                await self.redis.delete(*keys)
        except Exception:
            logger.warning("semantic cache invalidation failed", exc_info=True)

    async def close(self) -> None:
        # The default client is a shared pool and must stay alive between
        # requests.  Application lifespan closes it once during shutdown.
        if not self._owned:
            return
        try:
            await self.redis.aclose()
        except Exception:
            logger.debug("semantic cache close failed", exc_info=True)


async def close_cache_redis() -> None:
    redis = get_cache_redis.cache_info()
    if redis.currsize:
        client = get_cache_redis()
        await client.aclose()
        get_cache_redis.cache_clear()
