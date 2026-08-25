import pytest


from app.tools.knowledge_search import (
    KnowledgeSearchTool,
)



class FakeRagService:


    async def chat(
        self,
        question,
        user_id,
    ):

        return (
            "退款政策需要7天内申请"
        )



@pytest.mark.asyncio
async def test_knowledge_search_tool():


    tool = KnowledgeSearchTool(
        FakeRagService()
    )


    result = await tool.execute(

        {
            "question":
            "退款政策是什么"
        },

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace001",
    )


    assert (
        result["success"]
        is True
    )


    assert (
        "退款"
        in result["answer"]
    )