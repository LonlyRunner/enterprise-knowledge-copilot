from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.rag.models import DocumentChunk


@dataclass
class RerankResult:
    chunk: DocumentChunk
    score: float
    original_rank: int


class BaseReranker(ABC):

    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: list[DocumentChunk],
        top_k: int,
    ) -> list[RerankResult]:
        pass