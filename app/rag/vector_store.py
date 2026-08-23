import math

from app.rag.models import (
    SearchResult,
    VectorDocument,
    DocumentChunk,
)


class InMemoryVectorStore:

    def __init__(self):
        self.documents: list[
            VectorDocument
        ] = []

    def add(
        self,
        documents: list[VectorDocument],
    ) -> None:

        self.documents.extend(
            documents
        )

    def clear(self) -> None:
        self.documents.clear()

    def size(self) -> int:
        return len(self.documents)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[SearchResult]:

        results: list[
            SearchResult
        ] = []

        for document in self.documents:

            score = self.cosine_similarity(
                query_embedding,
                document.embedding,
            )

            results.append(
                SearchResult(
                    chunk=document.chunk,
                    score=score,
                )
            )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:

        if len(vector_a) != len(vector_b):
            raise ValueError(
                "Vector dimensions do not match"
            )

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b,
            )
        )

        norm_a = math.sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )

        norm_b = math.sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (
            norm_a * norm_b
        )