import pytest


from app.rag.service import RagService
from app.llm.base import (
    LLMResult,
    TokenUsage,
)



class FakeLLMClient:

    async def chat(
        self,
        message: str,
    ):

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



@pytest.fixture
def fake_llm_client():

    return FakeLLMClient()