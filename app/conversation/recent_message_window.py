from __future__ import annotations

from dataclasses import dataclass

from app.conversation.token_counter import TokenCounter


@dataclass(frozen=True)
class RecentMessageWindowResult:
    """
    RecentMessageWindowResult（最近消息窗口结果）

    selected_messages:
        真正被选入 Context 的消息。

    used_tokens:
        被选消息一共使用多少 Token。

    budget:
        当前窗口允许使用的 Token Budget。

    dropped_messages:
        因预算限制没有进入 Context 的历史消息数量。
    """

    selected_messages: list[dict[str, str]]

    used_tokens: int

    budget: int

    dropped_messages: int

    @property
    def remaining_tokens(self) -> int:
        return max(
            0,
            self.budget - self.used_tokens,
        )


class RecentMessageWindow:
    """
    RecentMessageWindow（最近消息窗口）

    从 Conversation History 的最后一条消息开始，
    按照 Token Budget 向前选择尽可能多的历史消息。
    """

    def __init__(
        self,
        token_counter: TokenCounter,
    ):
        self.token_counter = token_counter

    def select(
        self,
        messages: list[dict[str, str]],
        token_budget: int,
    ) -> RecentMessageWindowResult:

        if token_budget < 0:
            raise ValueError(
                "token_budget cannot be negative"
            )

        if not messages:
            return RecentMessageWindowResult(
                selected_messages=[],
                used_tokens=0,
                budget=token_budget,
                dropped_messages=0,
            )

        selected_reversed: list[
            dict[str, str]
        ] = []

        used_tokens = 0

        # 从最新的 Message 开始向前扫描
        for message in reversed(messages):

            role = message.get(
                "role",
                "user",
            )

            content = message.get(
                "content",
                "",
            )

            message_tokens = (
                self.token_counter.count_message(
                    role=role,
                    content=content,
                )
            )

            # 加入当前消息后会超预算
            if (
                used_tokens + message_tokens
                > token_budget
            ):
                break

            selected_reversed.append(
                {
                    "role": role,
                    "content": content,
                }
            )

            used_tokens += message_tokens

        # 因为前面是从后往前选择，
        # 最后需要恢复聊天的正常时间顺序。
        selected_messages = list(
            reversed(selected_reversed)
        )

        dropped_messages = (
            len(messages)
            - len(selected_messages)
        )

        return RecentMessageWindowResult(
            selected_messages=selected_messages,
            used_tokens=used_tokens,
            budget=token_budget,
            dropped_messages=dropped_messages,
        )