from dataclasses import dataclass

from app.rag.context import (
    ContextDegrader,
    RagRuntimeContext,
)


@dataclass
class MockMessage:
    role: str
    content: str


@dataclass
class TestChunk:
    content: str


def build_context(
    *,
    history,
    rag_chunks,
):
    return RagRuntimeContext(
        summary="测试摘要",
        history=history,
        rag_chunks=rag_chunks,
        question="那超过两万呢？",
        summary_tokens=10,
        history_tokens=100,
        rag_context_tokens=100,
        question_tokens=10,
        history_budget=1000,
        rag_context_budget=1000,
        history_truncated=False,
        rag_context_truncated=False,
    )


def test_degrader_removes_lowest_ranked_rag_first():
    degrader = ContextDegrader()

    context = build_context(
        history=[
            MockMessage(
                role="user",
                content="最近问题",
            )
        ],
        rag_chunks=[
            TestChunk(content="高相关"),
            TestChunk(content="中相关"),
            TestChunk(content="低相关"),
        ],
    )

    degraded = degrader.degrade(context)

    assert degraded is not None
    assert len(degraded.rag_chunks) == 2
    assert degraded.rag_chunks[-1].content == "中相关"

    # History 此时不应该动
    assert len(degraded.history) == 1


def test_degrader_removes_oldest_history_when_no_rag():
    degrader = ContextDegrader()

    context = build_context(
        history=[
            MockMessage(
                role="user",
                content="最旧问题",
            ),
            MockMessage(
                role="assistant",
                content="最近回答",
            ),
        ],
        rag_chunks=[],
    )

    degraded = degrader.degrade(context)

    assert degraded is not None
    assert len(degraded.history) == 1
    assert degraded.history[0].content == "最近回答"


def test_degrader_returns_none_when_nothing_left():
    degrader = ContextDegrader()

    context = build_context(
        history=[],
        rag_chunks=[],
    )

    degraded = degrader.degrade(context)

    assert degraded is None