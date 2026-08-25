import pytest


from app.agent.langgraph.graph import (
    create_customer_graph,
)



@pytest.mark.asyncio
async def test_order_graph():


    graph = (
        create_customer_graph()
    )


    result = await graph.ainvoke(

        {
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
        "订单正在运输中"
    )



@pytest.mark.asyncio
async def test_knowledge_graph():


    graph = (
        create_customer_graph()
    )


    result = await graph.ainvoke(

        {
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