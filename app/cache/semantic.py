"""Redis-backed semantic/result cache used by stateless RAG queries."""
import hashlib
import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SemanticCache:
    def __init__(self, redis: Redis | None = None, ttl_seconds: int = 600):
        settings = get_settings()
        self.redis = redis or Redis.from_url(settings.redis_cache_url, decode_responses=True)
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
        try:
            await self.redis.aclose()
        except Exception:
            logger.debug("semantic cache close failed", exc_info=True)
