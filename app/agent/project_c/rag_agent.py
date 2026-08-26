from __future__ import annotations

from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts import AgentCitation
from app.gateway.schemas import GatewayRequest
from app.rag.service import RagService


class ProjectCRagAgent:
    def __init__(self, service_factory: Callable[[AsyncSession], RagService] = RagService):
        self.service_factory = service_factory

    async def run(self, request: GatewayRequest, session: AsyncSession, *, tenant_id: str | None = None) -> dict:
        if request.knowledge_base_id is None:
            return {"status": "skipped", "summary": "未提供知识库，跳过 RAG", "answer": "", "citations": []}

        service = self.service_factory(session)
        try:
            response = await service.query(
                knowledge_base_id=request.knowledge_base_id,
                question=request.question,
                top_k=request.top_k,
                tenant_id=tenant_id,
            )
        finally:
            await service.close()

        citations = [
            AgentCitation(
                source=item.source,
                content=item.content,
                score=item.score,
                chunk_id=item.chunk_id or f"{item.source}:{item.chunk_index}",
            )
            for item in response.sources
        ]
        return {
            "status": "completed",
            "summary": f"检索到 {len(citations)} 条知识库引用",
            "answer": response.answer,
            "citations": citations,
        }
