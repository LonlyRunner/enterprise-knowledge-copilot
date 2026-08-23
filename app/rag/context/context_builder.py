from dataclasses import dataclass
from typing import Protocol

from app.rag.context.history_selector import (
    TokenAwareHistorySelector,
)
from app.rag.context.rag_context_selector import (
    TokenAwareRagContextSelector,
)
from app.rag.context.token_budget import (
    TokenBudget,
)
from app.rag.context.token_counter import (
    TokenCounter,
)


class MessageLike(Protocol):
    role: str
    content: str


class ChunkLike(Protocol):
    content: str


@dataclass(frozen=True)
class RagRuntimeContext:
    summary: str | None
    history: list[MessageLike]
    rag_chunks: list[ChunkLike]
    question: str

    summary_tokens: int
    history_tokens: int
    rag_context_tokens: int
    question_tokens: int

    history_budget: int
    rag_context_budget: int

    history_truncated: bool
    rag_context_truncated: bool

    @property
    def total_tokens(
        self,
    ) -> int:

        return (
            self.summary_tokens
            + self.history_tokens
            + self.rag_context_tokens
            + self.question_tokens
        )


class ContextBuilder:
    """
    Token-aware RAG Runtime Context Builder.

    负责：
    1. Conversation Summary
    2. Recent Message History
    3. Current Question
    4. RAG Retrieved Context
    """

    def __init__(
        self,
        token_counter: TokenCounter,
        token_budget: TokenBudget,
        history_selector: TokenAwareHistorySelector,
        rag_context_selector: TokenAwareRagContextSelector,
    ) -> None:

        self.token_counter = (
            token_counter
        )

        self.token_budget = (
            token_budget
        )

        self.history_selector = (
            history_selector
        )

        self.rag_context_selector = (
            rag_context_selector
        )

    def build_conversation_context(
        self,
        *,
        summary: str | None,
        history_candidates: list[MessageLike],
        question: str,
    ) -> RagRuntimeContext:

        summary_tokens = (
            self.token_counter.count_text(
                summary
            )
        )

        question_tokens = (
            self.token_counter.count_text(
                question
            )
        )

        history_budget = (
            self._calculate_history_budget(
                summary_tokens=(
                    summary_tokens
                ),
                question_tokens=(
                    question_tokens
                ),
            )
        )

        history_selection = (
            self.history_selector.select(
                messages=(
                    history_candidates
                ),
                budget_tokens=(
                    history_budget
                ),
            )
        )

        return RagRuntimeContext(
            summary=summary,
            history=(
                history_selection.messages
            ),
            rag_chunks=[],
            question=question,
            summary_tokens=(
                summary_tokens
            ),
            history_tokens=(
                history_selection.used_tokens
            ),
            rag_context_tokens=0,
            question_tokens=(
                question_tokens
            ),
            history_budget=(
                history_budget
            ),
            rag_context_budget=(
                self.token_budget
                .rag_context_budget
            ),
            history_truncated=(
                history_selection.truncated
            ),
            rag_context_truncated=False,
        )

    def attach_rag_context(
        self,
        *,
        context: RagRuntimeContext,
        rag_candidates: list[ChunkLike],
    ) -> RagRuntimeContext:

        rag_budget = (
            self._calculate_rag_context_budget(
                context=context,
            )
        )

        rag_selection = (
            self.rag_context_selector.select(
                chunks=(
                    rag_candidates
                ),
                budget_tokens=(
                    rag_budget
                ),
            )
        )

        return RagRuntimeContext(
            summary=(
                context.summary
            ),
            history=(
                context.history
            ),
            rag_chunks=(
                rag_selection.chunks
            ),
            question=(
                context.question
            ),
            summary_tokens=(
                context.summary_tokens
            ),
            history_tokens=(
                context.history_tokens
            ),
            rag_context_tokens=(
                rag_selection.used_tokens
            ),
            question_tokens=(
                context.question_tokens
            ),
            history_budget=(
                context.history_budget
            ),
            rag_context_budget=(
                rag_budget
            ),
            history_truncated=(
                context.history_truncated
            ),
            rag_context_truncated=(
                rag_selection.truncated
            ),
        )

    def _calculate_history_budget(
        self,
        *,
        summary_tokens: int,
        question_tokens: int,
    ) -> int:

        budget = (
            self.token_budget.input_budget
            - self.token_budget.system_prompt_budget
            - self.token_budget.rag_context_budget
            - summary_tokens
            - question_tokens
        )

        return max(
            budget,
            0,
        )

    def _calculate_rag_context_budget(
        self,
        *,
        context: RagRuntimeContext,
    ) -> int:

        used_without_rag = (
            self.token_budget.system_prompt_budget
            + context.summary_tokens
            + context.history_tokens
            + context.question_tokens
        )

        remaining = (
            self.token_budget.input_budget
            - used_without_rag
        )

        return max(
            min(
                remaining,
                self.token_budget.rag_context_budget,
            ),
            0,
        )