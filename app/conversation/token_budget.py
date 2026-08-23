from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenBudget:
    """
    TokenBudget（Token 预算）

    用于描述一次 LLM 请求中，
    Context Window 如何分配。
    """

    context_window: int

    output_reserve: int

    system_prompt_budget: int

    summary_budget: int

    recent_messages_budget: int

    retrieved_context_budget: int

    current_question_budget: int

    safety_buffer: int = 512

    def __post_init__(self):
        values = {
            "context_window": self.context_window,
            "output_reserve": self.output_reserve,
            "system_prompt_budget": self.system_prompt_budget,
            "summary_budget": self.summary_budget,
            "recent_messages_budget": self.recent_messages_budget,
            "retrieved_context_budget": self.retrieved_context_budget,
            "current_question_budget": self.current_question_budget,
            "safety_buffer": self.safety_buffer,
        }

        for name, value in values.items():
            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative"
                )

        if self.total_reserved > self.context_window:
            raise ValueError(
                "Token budget exceeds model context window: "
                f"{self.total_reserved} > "
                f"{self.context_window}"
            )

    @property
    def input_budget(self) -> int:
        """
        真正允许 Input 使用的最大 Token。
        """

        return (
            self.context_window
            - self.output_reserve
            - self.safety_buffer
        )

    @property
    def allocated_input_budget(self) -> int:
        """
        已经明确分配给各 Input Component 的 Token。
        """

        return (
            self.system_prompt_budget
            + self.summary_budget
            + self.recent_messages_budget
            + self.retrieved_context_budget
            + self.current_question_budget
        )

    @property
    def unallocated_input_budget(self) -> int:
        """
        当前剩余但还没有分配的 Input Token。
        """

        return (
            self.input_budget
            - self.allocated_input_budget
        )

    @property
    def total_reserved(self) -> int:
        """
        所有预算总和。
        """

        return (
            self.output_reserve
            + self.safety_buffer
            + self.allocated_input_budget
        )

    def can_fit_input(
        self,
        token_count: int,
    ) -> bool:
        return token_count <= self.input_budget


DEFAULT_TOKEN_BUDGET = TokenBudget(
    context_window=32768,
    output_reserve=4096,
    system_prompt_budget=1500,
    summary_budget=3000,
    recent_messages_budget=6000,
    retrieved_context_budget=12000,
    current_question_budget=1000,
    safety_buffer=512,
)