from dataclasses import dataclass

from app.rag.bm25 import (
    BM25Retriever,
)
from app.rag.embedding import (
    EmbeddingClient,
)
from app.rag.models import (
    SearchResult,
)
from app.repositories.vector import (
    PostgresVectorRepository,
)
import uuid

@dataclass
class HybridSearchResult:
    chunk_id: str
    result: SearchResult
    vector_rank: int | None
    bm25_rank: int | None
    rrf_score: float


class HybridRetriever:

    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_repository: PostgresVectorRepository,
        bm25_retriever: BM25Retriever,
        rrf_k: int = 60,
    ):
        self.embedding_client = (
            embedding_client
        )

        self.vector_repository = (
            vector_repository
        )

        self.bm25_retriever = (
            bm25_retriever
        )

        self.rrf_k = rrf_k

    async def search(
            self,
            *,
            knowledge_base_id: uuid.UUID,
            query: str,
            top_k: int = 5,
            candidate_k: int = 10,
    ) -> list[HybridSearchResult]:

        query_embedding = (
            await self.embedding_client.embed(
                query
            )
        )

        vector_results = (
            await self.vector_repository.search(
                knowledge_base_id=(
                    knowledge_base_id
                ),
                query_embedding=(
                    query_embedding
                ),
                top_k=candidate_k,
            )
        )

        bm25_results = (
            self.bm25_retriever.search(
                query=query,
                top_k=candidate_k,
            )
        )

        merged: dict[
            str,
            HybridSearchResult
        ] = {}

        for rank, result in enumerate(
            vector_results,
            start=1,
        ):

            chunk_id = (
                result.chunk.id
            )

            merged[chunk_id] = (
                HybridSearchResult(
                    chunk_id=chunk_id,
                    result=result,
                    vector_rank=rank,
                    bm25_rank=None,
                    rrf_score=(
                        1
                        / (
                            self.rrf_k
                            + rank
                        )
                    ),
                )
            )

        for rank, result in enumerate(
            bm25_results,
            start=1,
        ):

            chunk_id = (
                result.chunk.id
            )

            score = (
                1
                / (
                    self.rrf_k
                    + rank
                )
            )

            if chunk_id in merged:

                merged[
                    chunk_id
                ].bm25_rank = rank

                merged[
                    chunk_id
                ].rrf_score += score

            else:

                merged[chunk_id] = (
                    HybridSearchResult(
                        chunk_id=chunk_id,
                        result=result,
                        vector_rank=None,
                        bm25_rank=rank,
                        rrf_score=score,
                    )
                )

        results = list(
            merged.values()
        )

        results.sort(
            key=lambda item: (
                item.rrf_score
            ),
            reverse=True,
        )

        return results[:top_k]