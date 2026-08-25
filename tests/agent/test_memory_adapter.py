import pytest


from app.agent.langchain.memory_adapter import (
    ConversationMemoryAdapter,
)


class FakeConversationService:


    async def get_detail(
        self,
        *,
        knowledge_base_id,
        conversation_id,
    ):

        class Message:

            def __init__(
                self,
                role,
                content,
            ):

                self.role = role
                self.content = content


        return {

            "messages":[

                Message(
                    "user",
                    "我的订单在哪里?"
                ),

                Message(
                    "assistant",
                    "订单正在运输"
                ),

            ]

        }



@pytest.mark.asyncio
async def test_memory_adapter():


    adapter = (
        ConversationMemoryAdapter(
            FakeConversationService()
        )
    )


    messages = await (
        adapter.load_history(
            knowledge_base_id="kb001",

            conversation_id="conv001",
        )
    )


    assert len(messages) == 2


    assert (
        messages[0].content
        ==
        "我的订单在哪里?"
    )


    assert (
        messages[1].content
        ==
        "订单正在运输"
    )