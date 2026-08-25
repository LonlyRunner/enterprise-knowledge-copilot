import pytest


from app.agent.langgraph.graph import (
    create_customer_graph,
)



class FakeOrderAgent:


    async def run(
        self,
        question,
        tenant_id=None,
        user_id=None,
        trace_id=None,
        **kwargs,
    ):

        return {

            "answer":
            "订单查询结果"

        }



class FakeRagAgent:


    async def run(
        self,
        question,
        tenant_id=None,
        user_id=None,
        trace_id=None,
        **kwargs,
    ):

        return {

            "answer":
            "知识库结果"

        }



def build_test_graph():

    return create_customer_graph(

        order_agent=(
            FakeOrderAgent()
        ),

        rag_agent=(
            FakeRagAgent()
        ),

    )



@pytest.mark.asyncio
async def test_human_review_interrupt():


    graph = (
        build_test_graph()
    )


    config = {

        "configurable":
        {

            "thread_id":
            "refund001"

        }

    }


    result = await graph.ainvoke(

        {

            "question":
            "我要退款订单",

            "intent":
            "order",

            "answer":
            None,

            "tenant_id":
            "tenant001",

            "user_id":
            "user001",

            "trace_id":
            "trace001",

            "need_human_review":
            False,

            "human_action":
            None,

        },

        config=config,

    )


    assert (
        "__interrupt__"
        in result
    )