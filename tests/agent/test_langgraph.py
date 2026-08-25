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
            "订单运输中"
        }



class FakeRagAgent:


    async def run(
        self,
        question,
        **kwargs,
    ):

        return {
            "answer":
            "公司退款政策如下"
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
async def test_order_graph():


    graph = build_test_graph()


    result = await graph.ainvoke(

        {
            "tenant_id":
            "test-tenant",

            "user_id":
            "test-user",

            "trace_id":
            "test-trace",

            "question":
            "我的订单在哪里",

            "intent":
            None,

            "answer":
            None,
        }

    )


    assert (
        result["intent"]
        ==
        "order"
    )


    assert (
        result["answer"]
        ==
        "订单运输中"
    )



@pytest.mark.asyncio
async def test_knowledge_graph():


    graph = build_test_graph()


    result = await graph.ainvoke(

        {
            "tenant_id":
            "test-tenant",

            "user_id":
            "test-user",

            "trace_id":
            "test-trace",

            "question":
            "公司的退款政策",

            "intent":
            None,

            "answer":
            None,
        }

    )


    assert (
        result["intent"]
        ==
        "knowledge"
    )


    assert (
        result["answer"]["answer"]
        ==
        "公司退款政策如下"
    )