"""Small async retry helpers shared by outbound AI clients."""
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int,
    base_delay: float,
    is_retryable: Callable[[Exception], bool],
) -> T:
    """Retry transient failures with capped exponential backoff and jitter."""
    attempts = max(1, attempts)
    last_error: Exception | None = None
    for index in range(attempts):
        try:
            return await operation()
        except Exception as exc:  # callback decides whether it is transient
            last_error = exc
            if index >= attempts - 1 or not is_retryable(exc):
                raise
            delay = min(base_delay * (2**index), 8.0)
            await asyncio.sleep(delay * (0.8 + random.random() * 0.4))
    assert last_error is not None
    raise last_error
