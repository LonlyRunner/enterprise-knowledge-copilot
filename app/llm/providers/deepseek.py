import asyncio
import json
from collections.abc import AsyncIterator
import httpx

from app.core.config import get_settings
from app.core.exceptions import (
    LLMAuthenticationException,
    LLMRateLimitException,
    LLMServiceException,
    LLMTimeoutException,
)
from app.llm.base import (
    BaseLLMClient,
    LLMResult,
    TokenUsage, ToolCall, LLMMessage,
)


class DeepSeekLLMClient(BaseLLMClient):

    def __init__(self):
        self.settings = get_settings()

        self.api_key = self.settings.deepseek_api_key
        self.base_url = self.settings.deepseek_base_url.rstrip("/")
        self.model = self.settings.deepseek_model

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                self.settings.llm_timeout
            ),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _payload(
        self,
        message: str,
        stream: bool = False,
    ) -> dict:

        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an enterprise knowledge assistant. "
                        "Answer accurately and clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            "temperature": self.settings.llm_temperature,
            "stream": stream,
        }

    async def chat(
        self,
        message: str,
    ) -> LLMResult:

        url = f"{self.base_url}/chat/completions"

        for attempt in range(3):

            try:
                response = await self.client.post(
                    url=url,
                    headers=self._headers(),
                    json=self._payload(message),
                )

                self._check_response(response)

                data = response.json()

                usage_data = data.get("usage", {})

                usage = TokenUsage(
                    prompt_tokens=usage_data.get(
                        "prompt_tokens",
                        0,
                    ),
                    completion_tokens=usage_data.get(
                        "completion_tokens",
                        0,
                    ),
                    total_tokens=usage_data.get(
                        "total_tokens",
                        0,
                    ),
                )

                return LLMResult(
                    content=data["choices"][0]["message"]["content"],
                    model=data.get("model", self.model),
                    provider="deepseek",
                    usage=usage,
                )

            except httpx.TimeoutException:
                if attempt == 2:
                    raise LLMTimeoutException()

            except httpx.RequestError as exc:
                if attempt == 2:
                    raise LLMServiceException(
                        str(exc)
                    )

            await asyncio.sleep(
                2 ** attempt
            )

        raise LLMServiceException()

    async def stream_chat(
            self,
            messages: str | list[dict[str, str]],
    ) -> AsyncIterator[str]:

        url = (
            f"{self.base_url}/chat/completions"
        )

        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": (
                self.settings.llm_temperature
            ),
            "stream": True,
        }

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
        }

        async with httpx.AsyncClient(
                timeout=self.settings.llm_timeout
        ) as client:

            async with client.stream(
                    "POST",
                    url,
                    headers=headers,
                    json=payload,
            ) as response:

                response.raise_for_status()

                async for line in (
                        response.aiter_lines()
                ):

                    if not line:
                        continue

                    if not line.startswith(
                            "data:"
                    ):
                        continue

                    data = (
                        line
                        .removeprefix(
                            "data:"
                        )
                        .strip()
                    )

                    if data == "[DONE]":
                        break

                    try:
                        event = (
                            json.loads(
                                data
                            )
                        )

                    except json.JSONDecodeError:
                        continue

                    choices = (
                            event.get(
                                "choices"
                            )
                            or []
                    )

                    if not choices:
                        continue

                    delta = (
                            choices[0]
                            .get(
                                "delta"
                            )
                            or {}
                    )

                    content = (
                        delta.get(
                            "content"
                        )
                    )

                    if content:
                        yield content

    def _check_response(
        self,
        response: httpx.Response,
    ) -> None:

        if response.status_code == 401:
            raise LLMAuthenticationException()

        if response.status_code == 429:
            raise LLMRateLimitException()

        if response.status_code >= 500:
            raise LLMServiceException()

        if response.status_code >= 400:
            raise LLMServiceException(
                response.text
            )

    async def close(self):
        await self.client.aclose()

    async def chat_with_tools(
            self,
            messages,
            tools,
    ):

        payload = {

            "model":
                self.model,

            "messages":
                messages,

            "tools":
                tools,

            "temperature":
                0,

        }

        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=self._headers(),
        )

        self._check_response(response)

        data = response.json()

        message = (
            data["choices"][0]["message"]
        )

        tool_calls = []

        for call in message.get(
                "tool_calls",
                []
        ):
            tool_calls.append(

                ToolCall(

                    id=call["id"],

                    name=
                    call["function"]["name"],

                    arguments=
                    json.loads(
                        call["function"]["arguments"]
                    ),
                )
            )

        return LLMMessage(

            role="assistant",

            content=
            message.get("content"),

            tool_calls=tool_calls,
        )