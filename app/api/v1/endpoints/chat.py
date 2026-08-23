import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)



from app.services.chat_service import ChatService

router = APIRouter()

chat_service = ChatService()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:

    return await chat_service.chat(
        request.message
    )


@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
):

    async def event_generator():

        async for chunk in chat_service.stream_chat(
            request.message
        ):

            data = json.dumps(
                {
                    "content": chunk
                },
                ensure_ascii=False,
            )

            yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )