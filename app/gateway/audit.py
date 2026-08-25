import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.cache.semantic import get_cache_redis
from app.core.config import get_settings

logger = logging.getLogger("ai_gateway.audit")


class GatewayAuditLogger:
    def __init__(self, redis=None):
        self.redis = redis or get_cache_redis()
        self.settings = get_settings()

    async def write(self, event: str, *, trace_id: str, tenant_id: str, user_id: str, payload: dict[str, Any]) -> None:
        record = {
            "event": event,
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "payload": payload,
        }
        logger.info(json.dumps(record, ensure_ascii=False, default=str))
        key = f"ai-gateway:audit:{tenant_id}"
        try:
            await self.redis.lpush(key, json.dumps(record, ensure_ascii=False, default=str))
            await self.redis.ltrim(key, 0, 999)
            await self.redis.expire(key, self.settings.gateway_audit_ttl_seconds)
        except Exception:
            logger.warning("gateway audit redis persistence failed", exc_info=True)

