"""OpenAI-compatible embedding client with bounded batching and retries."""
import asyncio
import httpx
from functools import lru_cache

from app.core.config import get_settings
from app.core.exceptions import LLMRateLimitException, LLMServiceException, LLMTimeoutException
from app.core.retry import retry_async


class EmbeddingClient:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.embedding_api_key
        self.base_url = self.settings.embedding_base_url.rstrip("/")
        self.model = self.settings.embedding_model
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.embedding_timeout, connect=10.0, pool=10.0),
            limits=httpx.Limits(
                max_connections=self.settings.http_max_connections,
                max_keepalive_connections=self.settings.http_max_keepalive_connections,
                keepalive_expiry=self.settings.http_keepalive_expiry_seconds,
            ),
            trust_env=False,
        )

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        batch_size = max(1, self.settings.embedding_batch_size)
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        semaphore = asyncio.Semaphore(max(1, self.settings.embedding_max_concurrency))

        async def run_batch(batch: list[str]) -> list[list[float]]:
            async with semaphore:
                return await retry_async(
                    lambda: self._request_batch(batch),
                    attempts=self.settings.retry_max_attempts,
                    base_delay=self.settings.retry_base_delay_seconds,
                    is_retryable=self._is_retryable,
                )

        results = await asyncio.gather(*(run_batch(batch) for batch in batches))
        return [vector for batch in results for vector in batch]

    async def _request_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "input": texts, "dimensions": self.settings.embedding_dimensions},
            )
        except httpx.TimeoutException as exc:
            raise LLMTimeoutException() from exc
        except httpx.RequestError as exc:
            raise LLMServiceException(str(exc)) from exc

        if response.status_code == 429:
            raise LLMRateLimitException()
        if response.status_code >= 500 or response.status_code == 408:
            error = LLMServiceException(f"Embedding request failed: {response.status_code}")
            error.retryable = True
            raise error
        if response.status_code >= 400:
            raise LLMServiceException(f"Embedding request failed: {response.status_code} {response.text}")

        try:
            items = sorted(response.json()["data"], key=lambda item: item.get("index", 0))
            embeddings = [item["embedding"] for item in items]
        except (KeyError, TypeError, ValueError) as exc:
            raise LLMServiceException("Invalid embedding response") from exc
        if len(embeddings) != len(texts):
            raise LLMServiceException(f"Embedding count mismatch: expected {len(texts)}, got {len(embeddings)}")
        expected_dimension = self.settings.embedding_dimensions
        for vector in embeddings:
            if len(vector) != expected_dimension:
                raise LLMServiceException(
                    f"Embedding dimension mismatch: expected {expected_dimension}, got {len(vector)}"
                )
        return embeddings

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        if isinstance(exc, (httpx.TimeoutException, httpx.RequestError, LLMRateLimitException, LLMTimeoutException)):
            return True
        return isinstance(exc, LLMServiceException) and bool(getattr(exc, "retryable", False))

    async def close(self) -> None:
        await self.client.aclose()


@lru_cache(maxsize=1)
def get_shared_embedding_client() -> EmbeddingClient:
    """Reuse the embedding HTTP connection pool for the process lifetime."""
    return EmbeddingClient()


async def close_shared_embedding_client() -> None:
    if get_shared_embedding_client.cache_info().currsize:
        await get_shared_embedding_client().close()
        get_shared_embedding_client.cache_clear()
