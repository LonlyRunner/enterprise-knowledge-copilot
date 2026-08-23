from dataclasses import dataclass


@dataclass(frozen=True)
class TokenBudget:
    """
    Context Window Token Budget.

    当前数值是项目初始预算，
    后续可以迁移到 Settings / .env。
    """

    model_context_window: int = 32768

    # 必须提前给模型回答预留空间
    reserved_output_tokens: int = 4096

    # System Prompt 最大预算
    system_prompt_budget: int = 2000

    # RAG 检索结果最大预算
    rag_context_budget: int = 12000

    # Conversation Summary 最大预算
    summary_budget: int = 3000

    # 当前问题预算
    current_question_budget: int = 1000

    @property
    def input_budget(self) -> int:
        """
        整个输入最多允许使用多少 Token。
        """
        return self.model_context_window - self.reserved_output_tokens

    @property
    def history_budget(self) -> int:
        """
        Conversation History 可以使用的最大 Token。
        """
        budget = (
            self.input_budget
            - self.system_prompt_budget
            - self.rag_context_budget
            - self.summary_budget
            - self.current_question_budget
        )

        return max(budget, 0)

    def as_dict(self) -> dict[str, int]:
        return {
            "model_context_window": self.model_context_window,
            "reserved_output_tokens": self.reserved_output_tokens,
            "input_budget": self.input_budget,
            "system_prompt_budget": self.system_prompt_budget,
            "rag_context_budget": self.rag_context_budget,
            "summary_budget": self.summary_budget,
            "current_question_budget": self.current_question_budget,
            "history_budget": self.history_budget,
        }