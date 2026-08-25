from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Any

@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResult:
    content: str
    model: str
    provider: str
    usage: TokenUsage


class BaseLLMClient(ABC):

    @abstractmethod
    async def chat(
        self,
        message: str,
    ) -> LLMResult:
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: str | list[dict[str, str]],
    ):
        pass

    async def chat_with_tools(
            self,
            messages: list[dict],
            tools: list[dict],
    ) -> LLMMessage:
        """
        支持工具调用的LLM接口
        """

        raise NotImplementedError


@dataclass
class ToolCall:
    """
    LLM返回的工具调用
    """

    id: str

    name: str

    arguments: dict[str, Any]



@dataclass
class LLMMessage:
    """
    Agent内部消息
    """

    role: str

    content: str | None = None

    tool_calls: list[ToolCall] | None = None
