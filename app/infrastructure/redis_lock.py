import uuid

from redis.asyncio import Redis


_RELEASE_LOCK_SCRIPT = """
if redis.call(
    "get",
    KEYS[1]
) == ARGV[1] then
    return redis.call(
        "del",
        KEYS[1]
    )
else
    return 0
end
"""


class RedisDistributedLock:

    def __init__(
        self,
        *,
        redis_url: str,
        key: str,
        ttl_seconds: int = 300,
    ):
        self.redis_url = (
            redis_url
        )

        self.key = key

        self.ttl_seconds = (
            ttl_seconds
        )

        self.token = str(
            uuid.uuid4()
        )

        self.redis: (
            Redis | None
        ) = None

        self.acquired = False

    async def acquire(
        self,
    ) -> bool:

        self.redis = (
            Redis.from_url(
                self.redis_url,
                decode_responses=True,
            )
        )

        result = (
            await self.redis.set(
                self.key,
                self.token,
                nx=True,
                ex=self.ttl_seconds,
            )
        )

        self.acquired = bool(
            result
        )

        return self.acquired

    async def release(
        self,
    ) -> None:

        if (
            not self.redis
            or not self.acquired
        ):
            return

        try:

            await self.redis.eval(
                _RELEASE_LOCK_SCRIPT,
                1,
                self.key,
                self.token,
            )

        finally:

            self.acquired = False

    async def close(
        self,
    ) -> None:

        if self.redis:

            await self.redis.aclose()

            self.redis = None

    async def __aenter__(
            self,
    ):

        acquired = await self.acquire()

        if not acquired:
            raise RuntimeError(
                f"Failed to acquire lock: {self.key}"
            )

        return self

    async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
    ):

        try:

            await self.release()

        finally:

            await self.close()