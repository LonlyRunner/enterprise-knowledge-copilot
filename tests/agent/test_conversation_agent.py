import pytest


from app.agent.langchain.conversation_agent import (
    ConversationAgent,
)



class FakeMemory:


    async def load_history(
        self,
        **kwargs,
    ):

        return []


class FakeAgent:


    async def ainvoke(
        self,
        data,
    ):

        return {

            "messages":
            data["messages"]

        }



@pytest.mark.asyncio
async def test_conversation_agent():


    agent = ConversationAgent(

        agent=FakeAgent(),

        memory_adapter=FakeMemory(),

    )


    result = await agent.run(

        question="你好",

        knowledge_base_id="kb",

        conversation_id="conv",

    )


    assert (
        len(
            result["messages"]
        )
        ==
        1
    )