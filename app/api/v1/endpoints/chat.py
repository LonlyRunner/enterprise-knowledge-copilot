from collections.abc import AsyncIterator
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.client import (
    create_llm_client,
)
from app.utils.sse import (
    encode_sse,
)
from app.auth.rbac import require_permission
from app.auth.models import User
from app.db.dependencies import get_db
from app.rag.service import RagService
from app.schemas.rag import RagChatRequest
from app.core.config import get_settings


router = APIRouter()
logger = logging.getLogger(__name__)

llm_client = create_llm_client()


async def close_llm_client() -> None:
    await llm_client.close()


@router.post(
    "/stream-test"
)
async def stream_test(user: User = Depends(require_permission("diagnostics:run"))):
    if not get_settings().diagnostics_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    async def event_generator(
    ) -> AsyncIterator[str]:

        yield encode_sse(
            "start",
            {},
        )

        try:

            messages = [
                {
                    "role": "user",
                    "content": (
                        "4000元报销需要哪些人审批？"
                    ),
                }
            ]

            async for content in (
                llm_client.stream_chat(
                    messages=messages,
                )
            ):

                yield encode_sse(
                    "delta",
                    {
                        "content": (
                            content
                        ),
                    },
                )

            yield encode_sse(
                "done",
                {},
            )

        except Exception:
            logger.exception("diagnostic stream failed")

            yield encode_sse(
                "error",
                {
                    "message": "Diagnostic stream failed",
                    "code": "DIAGNOSTIC_STREAM_ERROR",
                },
            )

    return StreamingResponse(
        event_generator(),
        media_type=(
            "text/event-stream"
        ),
        headers={
            "Cache-Control": (
                "no-cache"
            ),
            "Connection": (
                "keep-alive"
            ),
        },
    )


@router.post("/rag/chat/stream")
async def rag_chat_stream(
    request: RagChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("chat:use")),
    http_request: Request = None,
):
    """Return the same persisted RAG answer using a stable SSE contract."""
    async def event_generator() -> AsyncIterator[str]:
        yield encode_sse("start", {"conversation_id": str(request.conversation_id)})
        try:
            service = RagService(session=db)
            async for event in service.chat_stream(
                knowledge_base_id=request.knowledge_base_id,
                conversation_id=request.conversation_id,
                question=request.question,
                top_k=request.top_k,
                tenant_id=user.tenant_id,
            ):
                if http_request is not None and await http_request.is_disconnected():
                    return
                yield encode_sse(event["event"], event["data"])
        except Exception:
            logger.exception("RAG stream failed")
            yield encode_sse("error", {"message": "RAG request failed", "code": "RAG_STREAM_ERROR"})
        finally:
            if "service" in locals():
                await service.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
