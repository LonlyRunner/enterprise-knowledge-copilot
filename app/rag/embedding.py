import httpx

from app.core.config import get_settings
from app.core.exceptions import LLMServiceException


class EmbeddingClient:

    def __init__(self):
        self.settings = get_settings()

        self.api_key = self.settings.embedding_api_key
        self.base_url = (
            self.settings.embedding_base_url.rstrip("/")
        )
        self.model = self.settings.embedding_model

        self.client = httpx.AsyncClient(
            timeout=self.settings.embedding_timeout,
            trust_env=False,

        )

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        embeddings = await self.embed_batch(
            [text]
        )

        return embeddings[0]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        response = await self.client.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": texts,
                "dimensions": self.settings.embedding_dimensions,
            },
        )

        if response.status_code >= 400:
            raise LLMServiceException(
                f"Embedding request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        items = data["data"]

        items = sorted(
            items,
            key=lambda item: item.get(
                "index",
                0,
            ),
        )

        embeddings = [
            item["embedding"]
            for item in items
        ]

        expected_dimension = self.settings.embedding_dimensions
        invalid = [
            len(vector)
            for vector in embeddings
            if len(vector) != expected_dimension
        ]
        if invalid:
            raise LLMServiceException(
                "Embedding dimension mismatch: "
                f"expected {expected_dimension}, got {invalid[0]}"
            )

        return embeddings

    async def close(self):
        await self.client.aclose()
