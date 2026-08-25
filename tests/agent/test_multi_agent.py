import pytest


from app.agent.multi.graph import (
    create_multi_agent_graph,
)



@pytest.mark.asyncio
async def test_order_agent():


    graph = (
        create_multi_agent_graph()
    )


    result = await graph.ainvoke(

        {
            "question":
            "我的订单在哪里",

            "next_agent":
            None,

            "answer":
            None,

            "history":
            [],
        }

    )


    assert (
        result["answer"]
        ==
        "订单正在运输"
    )