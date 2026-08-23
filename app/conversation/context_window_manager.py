from __future__ import annotations

from dataclasses import dataclass

from app.conversation.recent_message_window import (
    RecentMessageWindow,
)
from app.conversation.token_budget import (
    TokenBudget,
)
from app.conversation.token_counter import (
    TokenCounter,
)


@dataclass(frozen=True)
class ManagedContext:
    """
    ManagedContext（受管理上下文）

    表示一次 LLM 调用最终准备好的 Context。
    """

    system_prompt: str

    conversation_summary: str | None

    recent_messages: list[dict[str, str]]

    retrieved_context: list[str]

    current_question: str

    token_usage: dict[str, int]

    total_input_tokens: int


class ContextWindowManager:
    """
    ContextWindowManager（上下文窗口管理器）

    负责：

    1. 统计不同 Context Component 的 Token；
    2. 根据 TokenBudget 检查各部分预算；
    3. 对 Conversation History 应用 RecentMessageWindow；
    4. 构造最终 ManagedContext。
    """

    def __init__(
        self,
        token_counter: TokenCounter,
        token_budget: TokenBudget,
    ):
        self.token_counter = token_counter
        self.token_budget = token_budget

        self.recent_message_window = (
            RecentMessageWindow(
                token_counter=token_counter,
            )
        )

    def build(
        self,
        *,
        system_prompt: str,
        conversation_summary: str | None,
        messages: list[dict[str, str]],
        retrieved_context: list[str],
        current_question: str,
    ) -> ManagedContext:

        system_prompt_tokens = (
            self.token_counter.count_text(
                system_prompt
            )
        )

        self._validate_component_budget(
            name="system_prompt",
            token_count=system_prompt_tokens,
            budget=(
                self.token_budget
                .system_prompt_budget
            ),
        )

        summary_tokens = (
            self.token_counter.count_text(
                conversation_summary
            )
        )

        self._validate_component_budget(
            name="conversation_summary",
            token_count=summary_tokens,
            budget=(
                self.token_budget.summary_budget
            ),
        )

        current_question_tokens = (
            self.token_counter.count_text(
                current_question
            )
        )

        self._validate_component_budget(
            name="current_question",
            token_count=current_question_tokens,
            budget=(
                self.token_budget
                .current_question_budget
            ),
        )

        recent_window_result = (
            self.recent_message_window.select(
                messages=messages,
                token_budget=(
                    self.token_budget
                    .recent_messages_budget
                ),
            )
        )

        selected_retrieved_context: list[str] = []

        retrieved_context_tokens = 0

        for context in retrieved_context:
            context_tokens = (
                self.token_counter.count_text(
                    context
                )
            )

            if (
                retrieved_context_tokens
                + context_tokens
                > self.token_budget
                .retrieved_context_budget
            ):
                break

            selected_retrieved_context.append(
                context
            )

            retrieved_context_tokens += (
                context_tokens
            )

        total_input_tokens = (
            system_prompt_tokens
            + summary_tokens
            + recent_window_result.used_tokens
            + retrieved_context_tokens
            + current_question_tokens
        )

        if not self.token_budget.can_fit_input(
            total_input_tokens
        ):
            raise ValueError(
                "Managed context exceeds "
                "total input token budget: "
                f"{total_input_tokens} > "
                f"{self.token_budget.input_budget}"
            )

        return ManagedContext(
            system_prompt=system_prompt,

            conversation_summary=(
                conversation_summary
            ),

            recent_messages=(
                recent_window_result
                .selected_messages
            ),

            retrieved_context=(
                selected_retrieved_context
            ),

            current_question=current_question,

            token_usage={
                "system_prompt": (
                    system_prompt_tokens
                ),
                "conversation_summary": (
                    summary_tokens
                ),
                "recent_messages": (
                    recent_window_result
                    .used_tokens
                ),
                "retrieved_context": (
                    retrieved_context_tokens
                ),
                "current_question": (
                    current_question_tokens
                ),
            },

            total_input_tokens=(
                total_input_tokens
            ),
        )

    @staticmethod
    def _validate_component_budget(
        *,
        name: str,
        token_count: int,
        budget: int,
    ) -> None:

        if token_count > budget:
            raise ValueError(
                f"{name} exceeds token budget: "
                f"{token_count} > {budget}"
            )