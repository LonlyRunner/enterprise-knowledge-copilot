from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from app.rag.context.token_counter import TokenCounter


class MessageLike(Protocol):
    role: str
    content: str


@dataclass(frozen=True)
class HistorySelectionResult:
    messages: list[MessageLike]
    used_tokens: int
    budget_tokens: int
    truncated: bool


class TokenAwareHistorySelector:
    """
    根据 Token Budget 选择最近的 Conversation History。

    策略：
    1. 输入消息按照时间从旧到新排列。
    2. 从最新消息开始向前选择。
    3. Token 总量不能超过 history_budget。
    4. 最终恢复为旧 -> 新的正常对话顺序。
    """

    def __init__(
        self,
        token_counter: TokenCounter,
    ) -> None:
        self.token_counter = token_counter

    def select(
        self,
        messages: Sequence[MessageLike],
        budget_tokens: int,
    ) -> HistorySelectionResult:
        if budget_tokens <= 0:
            return HistorySelectionResult(
                messages=[],
                used_tokens=0,
                budget_tokens=budget_tokens,
                truncated=len(messages) > 0,
            )

        selected_reversed: list[MessageLike] = []
        used_tokens = 0

        for message in reversed(messages):
            message_tokens = self._count_message(message)

            if used_tokens + message_tokens > budget_tokens:
                break

            selected_reversed.append(message)
            used_tokens += message_tokens

        selected = list(reversed(selected_reversed))

        return HistorySelectionResult(
            messages=selected,
            used_tokens=used_tokens,
            budget_tokens=budget_tokens,
            truncated=len(selected) < len(messages),
        )

    def _count_message(
        self,
        message: MessageLike,
    ) -> int:
        return self.token_counter.count_messages(
            [
                {
                    "role": message.role,
                    "content": message.content,
                }
            ]
        )