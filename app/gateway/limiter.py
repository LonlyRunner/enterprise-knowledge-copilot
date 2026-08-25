import time

from redis.asyncio import Redis



class RateLimiter:


    def __init__(
        self,
        redis: Redis,
        limit: int = 60,
        window: int = 60,
    ):

        self.redis = redis

        self.limit = limit

        self.window = window



    async def check(
        self,
        key: str,
    ) -> bool:


        current = await self.redis.incr(
            key
        )


        if current == 1:

            await self.redis.expire(
                key,
                self.window,
            )


        return current <= self.limit