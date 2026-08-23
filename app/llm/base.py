from abc import ABC, abstractmethod
from dataclasses import dataclass


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
        message: str,
    ):
        pass