from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
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


router = APIRouter()

llm_client = create_llm_client()


@router.post(
    "/stream-test"
)
async def stream_test():

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

        except Exception as exc:

            yield encode_sse(
                "error",
                {
                    "message": str(
                        exc
                    ),
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
):
    """Return the same persisted RAG answer using a stable SSE contract."""
    async def event_generator() -> AsyncIterator[str]:
        yield encode_sse("start", {"conversation_id": str(request.conversation_id)})
        try:
            async for event in RagService(session=db).chat_stream(
                knowledge_base_id=request.knowledge_base_id,
                conversation_id=request.conversation_id,
                question=request.question,
                top_k=request.top_k,
            ):
                yield encode_sse(event["event"], event["data"])
        except Exception as exc:
            yield encode_sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
