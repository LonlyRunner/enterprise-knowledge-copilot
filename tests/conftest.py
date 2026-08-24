from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.llm.base import LLMResult, TokenUsage


class FakeLLMClient:
    async def chat(self, message: str) -> LLMResult:
        return LLMResult(
            content="测试答案",
            model="test-model",
            provider="test",
            usage=TokenUsage(
                prompt_tokens=100,
                completion_tokens=20,
                total_tokens=120,
            ),
        )


class FakeRagService:
    async def chat(self, *, knowledge_base_id, conversation_id, question, top_k=3):
        return {
            "conversation_id": conversation_id,
            "answer": "测试答案",
            "metrics": {
                "trace_id": "test-trace-id",
                "tokens": {"input": 10, "output": 5, "total": 15},
            },
        }


@pytest.fixture
def fake_llm_client():
    return FakeLLMClient()


@pytest.fixture
def rag_service():
    return FakeRagService()


@pytest.fixture
def conversation():
    return SimpleNamespace(id=uuid4(), knowledge_base_id=uuid4())
