import pytest

from app.rag.context import (
    BuiltPrompt,
    ContextWindowExceededError,
    TokenBudget,
    TokenCounter,
    TokenGuard,
)


def test_token_guard_accepts_normal_prompt():
    counter = TokenCounter()

    budget = TokenBudget(
        model_context_window=2000,
        reserved_output_tokens=500,
    )

    guard = TokenGuard(
        token_counter=counter,
        token_budget=budget,
    )

    prompt = BuiltPrompt(
        system_prompt="企业知识库助手",
        user_prompt="4000元报销需要哪些人审批？",
    )

    result = guard.validate(prompt)

    assert result.total_input_tokens <= result.input_budget
    assert result.remaining_tokens >= 0


def test_token_guard_rejects_oversized_prompt():
    counter = TokenCounter()

    budget = TokenBudget(
        model_context_window=200,
        reserved_output_tokens=50,
    )

    guard = TokenGuard(
        token_counter=counter,
        token_budget=budget,
    )

    prompt = BuiltPrompt(
        system_prompt="企业知识库助手",
        user_prompt="测试内容" * 1000,
    )

    with pytest.raises(ContextWindowExceededError):
        guard.validate(prompt)