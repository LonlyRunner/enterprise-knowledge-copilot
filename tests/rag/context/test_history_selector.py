from dataclasses import dataclass

from app.rag.context import (
    TokenAwareHistorySelector,
    TokenCounter,
)


@dataclass
class TestMessage:
    role: str
    content: str


def test_history_selector_keeps_recent_messages():
    counter = TokenCounter()

    selector = TokenAwareHistorySelector(
        token_counter=counter,
    )

    messages = [
        TestMessage(
            role="user",
            content="旧问题" * 100,
        ),
        TestMessage(
            role="assistant",
            content="旧回答" * 100,
        ),
        TestMessage(
            role="user",
            content="最近的问题",
        ),
    ]

    recent_tokens = counter.count_messages(
        [
            {
                "role": "user",
                "content": "最近的问题",
            }
        ]
    )

    result = selector.select(
        messages=messages,
        budget_tokens=recent_tokens + 5,
    )

    assert len(result.messages) == 1
    assert result.messages[0].content == "最近的问题"
    assert result.truncated is True


def test_history_selector_never_exceeds_budget():
    counter = TokenCounter()

    selector = TokenAwareHistorySelector(
        token_counter=counter,
    )

    messages = [
        TestMessage(
            role="user",
            content="4000元报销需要哪些人审批？" * 100,
        ),
        TestMessage(
            role="assistant",
            content="企业制度相关回答。" * 100,
        ),
    ]

    budget = 500

    result = selector.select(
        messages=messages,
        budget_tokens=budget,
    )

    assert result.used_tokens <= budget