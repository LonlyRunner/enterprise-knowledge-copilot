from dataclasses import dataclass
from typing import Protocol

from app.rag.context.history_selector import (
    HistorySelectionResult,
    TokenAwareHistorySelector,
)
from app.rag.context.token_budget import TokenBudget
from app.rag.context.token_counter import TokenCounter


class MessageLike(Protocol):
    role: str
    content: str


@dataclass(frozen=True)
class ConversationContext:
    """
    当前单轮 RAG 请求所使用的 Conversation Context。
    """

    summary: str | None
    history: list[MessageLike]
    question: str

    summary_tokens: int
    history_tokens: int
    question_tokens: int

    history_budget: int
    truncated: bool

    @property
    def total_tokens(self) -> int:
        return (
            self.summary_tokens
            + self.history_tokens
            + self.question_tokens
        )


class ContextBuilder:
    """
    Token-aware Conversation Context Builder.

    当前负责：
    1. Conversation Summary
    2. Recent Message History
    3. Current Question

    暂时不负责 RAG Retrieved Context。
    """

    def __init__(
        self,
        token_counter: TokenCounter,
        token_budget: TokenBudget,
        history_selector: TokenAwareHistorySelector,
    ) -> None:
        self.token_counter = token_counter
        self.token_budget = token_budget
        self.history_selector = history_selector

    def build(
        self,
        *,
        summary: str | None,
        history_candidates: list[MessageLike],
        question: str,
    ) -> ConversationContext:
        summary_tokens = self.token_counter.count_text(summary)
        question_tokens = self.token_counter.count_text(question)

        available_history_budget = self._calculate_history_budget(
            summary_tokens=summary_tokens,
            question_tokens=question_tokens,
        )

        history_selection: HistorySelectionResult = (
            self.history_selector.select(
                messages=history_candidates,
                budget_tokens=available_history_budget,
            )
        )

        return ConversationContext(
            summary=summary,
            history=history_selection.messages,
            question=question,
            summary_tokens=summary_tokens,
            history_tokens=history_selection.used_tokens,
            question_tokens=question_tokens,
            history_budget=available_history_budget,
            truncated=history_selection.truncated,
        )

    def _calculate_history_budget(
        self,
        *,
        summary_tokens: int,
        question_tokens: int,
    ) -> int:
        """
        根据 Summary 和当前 Question 的实际 Token 使用量，
        动态计算本轮 History 可以使用多少 Token。
        """

        budget = (
            self.token_budget.input_budget
            - self.token_budget.system_prompt_budget
            - self.token_budget.rag_context_budget
            - summary_tokens
            - question_tokens
        )

        return max(budget, 0)