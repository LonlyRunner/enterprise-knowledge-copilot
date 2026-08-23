from dataclasses import dataclass

from app.rag.context import (
    TokenAwareRagContextSelector,
    TokenCounter,
)


@dataclass
class TestChunk:
    content: str


def test_rag_selector_keeps_highest_ranked_chunks():
    counter = TokenCounter()

    selector = TokenAwareRagContextSelector(
        token_counter=counter,
    )

    chunks = [
        TestChunk(content="最高相关知识"),
        TestChunk(content="第二相关知识"),
        TestChunk(content="最低相关知识" * 500),
    ]

    first_two_tokens = (
        counter.count_text(chunks[0].content)
        + counter.count_text(chunks[1].content)
    )

    result = selector.select(
        chunks=chunks,
        budget_tokens=first_two_tokens + 5,
    )

    assert len(result.chunks) == 2
    assert result.chunks[0].content == "最高相关知识"
    assert result.chunks[1].content == "第二相关知识"
    assert result.truncated is True


def test_rag_selector_never_exceeds_budget():
    counter = TokenCounter()

    selector = TokenAwareRagContextSelector(
        token_counter=counter,
    )

    chunks = [
        TestChunk(
            content="公司报销审批制度。" * 200
        ),
        TestChunk(
            content="超过金额需要升级审批。" * 200
        ),
    ]

    budget = 300

    result = selector.select(
        chunks=chunks,
        budget_tokens=budget,
    )

    assert result.used_tokens <= budget