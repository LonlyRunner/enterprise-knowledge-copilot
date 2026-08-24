from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.llm.client import (
    create_llm_client,
)
from app.utils.sse import (
    encode_sse,
)


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