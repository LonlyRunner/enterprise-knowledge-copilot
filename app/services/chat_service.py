from app.llm.base import BaseLLMClient
from app.llm.client import create_llm_client
from app.schemas.chat import (
    ChatResponse,
    TokenUsageResponse,
)


class ChatService:

    def __init__(
        self,
        llm_client: BaseLLMClient | None = None,
    ):
        self.llm_client = (
            llm_client
            or create_llm_client()
        )

    async def chat(
        self,
        message: str,
    ) -> ChatResponse:

        result = await self.llm_client.chat(
            message
        )

        return ChatResponse(
            answer=result.content,
            model=result.model,
            provider=result.provider,
            usage=TokenUsageResponse(
                prompt_tokens=result.usage.prompt_tokens,
                completion_tokens=result.usage.completion_tokens,
                total_tokens=result.usage.total_tokens,
            ),
        )

    async def stream_chat(
        self,
        message: str,
    ):
        async for chunk in self.llm_client.stream_chat(
            message
        ):
            yield chunk