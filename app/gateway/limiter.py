import logging

from app.cache.semantic import get_cache_redis

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    def __init__(self, retry_after_seconds: int):
        self.retry_after_seconds = max(1, retry_after_seconds)
        super().__init__("AI Gateway rate limit exceeded")


class RedisRateLimiter:
    def __init__(self, redis=None):
        self.redis = redis or get_cache_redis()

    async def check(self, key: str, *, limit: int, window_seconds: int = 60) -> dict:
        if limit <= 0:
            return {"allowed": True, "remaining": -1, "retry_after": 0}
        redis_key = f"ai-gateway:rate:{key}"
        try:
            current = await self.redis.incr(redis_key)
            if current == 1:
                await self.redis.expire(redis_key, window_seconds)
            ttl = await self.redis.ttl(redis_key)
        except Exception:
            logger.warning("gateway rate limiter unavailable; request allowed", exc_info=True)
            return {"allowed": True, "remaining": limit, "retry_after": 0, "degraded": True}
        if current > limit:
            raise RateLimitExceeded(ttl if ttl > 0 else window_seconds)
        return {
            "allowed": True,
            "remaining": max(0, limit - current),
            "retry_after": 0,
        }

