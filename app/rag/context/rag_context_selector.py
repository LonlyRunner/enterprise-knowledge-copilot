from dataclasses import dataclass
from typing import Protocol

from app.rag.context.token_counter import TokenCounter


class ChunkLike(Protocol):
    content: str


@dataclass(frozen=True)
class RagContextSelectionResult:
    chunks: list[ChunkLike]
    used_tokens: int
    budget_tokens: int
    truncated: bool


class TokenAwareRagContextSelector:
    """
    根据 Token Budget 选择 RAG Chunks。

    输入 Chunk 必须已经按相关性从高到低排序。
    因此选择时从第一条开始依次加入。
    """

    def __init__(
        self,
        token_counter: TokenCounter,
    ) -> None:
        self.token_counter = token_counter

    def select(
        self,
        *,
        chunks: list[ChunkLike],
        budget_tokens: int,
    ) -> RagContextSelectionResult:
        if budget_tokens <= 0:
            return RagContextSelectionResult(
                chunks=[],
                used_tokens=0,
                budget_tokens=budget_tokens,
                truncated=len(chunks) > 0,
            )

        selected: list[ChunkLike] = []
        used_tokens = 0

        for chunk in chunks:
            chunk_tokens = self.token_counter.count_text(
                chunk.content
            )

            if used_tokens + chunk_tokens > budget_tokens:
                break

            selected.append(chunk)
            used_tokens += chunk_tokens

        return RagContextSelectionResult(
            chunks=selected,
            used_tokens=used_tokens,
            budget_tokens=budget_tokens,
            truncated=len(selected) < len(chunks),
        )