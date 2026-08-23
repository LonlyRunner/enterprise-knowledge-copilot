from dataclasses import dataclass

from app.rag.context.prompt_builder import BuiltPrompt
from app.rag.context.token_budget import TokenBudget
from app.rag.context.token_counter import TokenCounter


class ContextWindowExceededError(Exception):
    pass


@dataclass(frozen=True)
class TokenGuardResult:
    system_tokens: int
    user_tokens: int
    total_input_tokens: int
    input_budget: int

    @property
    def remaining_tokens(self) -> int:
        return max(
            self.input_budget - self.total_input_tokens,
            0,
        )


class TokenGuard:
    """
    最终 Prompt Token Guard。

    ContextBuilder 是预算规划。
    TokenGuard 是最终实际检查。
    """

    def __init__(
        self,
        *,
        token_counter: TokenCounter,
        token_budget: TokenBudget,
    ) -> None:
        self.token_counter = token_counter
        self.token_budget = token_budget

    def validate(
        self,
        prompt: BuiltPrompt,
    ) -> TokenGuardResult:
        system_tokens = self.token_counter.count_text(
            prompt.system_prompt
        )

        user_tokens = self.token_counter.count_text(
            prompt.user_prompt
        )

        total_input_tokens = (
            system_tokens
            + user_tokens
        )

        if total_input_tokens > self.token_budget.input_budget:
            raise ContextWindowExceededError(
                "Final prompt exceeds input token budget: "
                f"used={total_input_tokens}, "
                f"budget={self.token_budget.input_budget}"
            )

        return TokenGuardResult(
            system_tokens=system_tokens,
            user_tokens=user_tokens,
            total_input_tokens=total_input_tokens,
            input_budget=self.token_budget.input_budget,
        )