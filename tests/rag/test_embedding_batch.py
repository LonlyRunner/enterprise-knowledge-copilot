import pytest

from app.core.exceptions import LLMServiceException
from app.rag.embedding import EmbeddingClient


@pytest.mark.asyncio
async def test_embedding_client_splits_and_preserves_order(monkeypatch):
    client = EmbeddingClient()
    monkeypatch.setattr(client.settings, "embedding_batch_size", 2)
    monkeypatch.setattr(client.settings, "embedding_max_concurrency", 2)
    calls = []

    async def fake_request(texts):
        calls.append(list(texts))
        return [[float(int(text))] for text in texts]

    monkeypatch.setattr(client, "_request_batch", fake_request)
    try:
        result = await client.embed_batch(["1", "2", "3", "4", "5"])
    finally:
        await client.close()

    assert calls == [["1", "2"], ["3", "4"], ["5"]]
    assert result == [[1.0], [2.0], [3.0], [4.0], [5.0]]


@pytest.mark.asyncio
async def test_embedding_client_retries_transient_error(monkeypatch):
    client = EmbeddingClient()
    monkeypatch.setattr(client.settings, "retry_base_delay_seconds", 0)
    attempts = 0

    async def flaky_request(texts):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            error = LLMServiceException("temporary")
            error.retryable = True
            raise error
        return [[1.0] for _ in texts]

    monkeypatch.setattr(client, "_request_batch", flaky_request)
    try:
        result = await client.embed_batch(["hello"])
    finally:
        await client.close()

    assert attempts == 2
    assert result == [[1.0]]
