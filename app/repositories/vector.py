from dataclasses import dataclass
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import (
    DocumentChunkModel,
)
from app.rag.models import (
    DocumentChunk,
    SearchResult,
)

from app.models.document import (
    DocumentModel,
)


@dataclass
class VectorSearchRow:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    similarity: float


class PostgresVectorRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def search(
            self,
            *,
            knowledge_base_id: uuid.UUID,
            query_embedding: list[float],
            top_k: int = 5,
    ) -> list[SearchResult]:
        distance = (
            DocumentChunkModel.embedding
            .cosine_distance(
                query_embedding
            )
        )

        statement = (
            select(
                DocumentChunkModel,
                DocumentModel.name,
                distance.label(
                    "distance"
                ),
            )
            .join(
                DocumentModel,
                DocumentModel.id
                == DocumentChunkModel.document_id,
            )
            .where(
                DocumentModel.knowledge_base_id
                == knowledge_base_id
            )
            .order_by(
                distance.asc()
            )
            .limit(top_k)
        )

        result = await self.session.execute(
            statement
        )

        rows = result.all()

        search_results = []

        for (
                model,
                document_name,
                cosine_distance,
        ) in rows:
            similarity = (
                    1.0
                    - float(
                cosine_distance
            )
            )

            chunk = DocumentChunk(
                id=str(model.id),
                content=model.content,
                metadata={
                    "document_id": str(
                        model.document_id
                    ),
                    "chunk_index": (
                        model.chunk_index
                    ),
                    "source": (
                        document_name
                    ),
                    "knowledge_base_id": str(
                        knowledge_base_id
                    ),
                },
            )

            search_results.append(
                SearchResult(
                    chunk=chunk,
                    score=similarity,
                )
            )

        return search_results