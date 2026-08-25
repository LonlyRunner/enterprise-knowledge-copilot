import pytest


from app.agent.langgraph.graph import (
    create_customer_graph,
)

config = {

    "configurable":
    {
        "thread_id":
        "refund001"
    }

}

class FakeOrderAgent:


    async def run(
        self,
        *args,
        **kwargs,
    ):

        return {

            "answer":
            "订单处理中"

        }



class FakeRagAgent:


    async def run(
        self,
        question,
    ):

        return (
            "知识库回答"
        )



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
    graph = await (
        create_customer_graph(

            FakeOrderAgent(),

            FakeRagAgent(),

        )
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