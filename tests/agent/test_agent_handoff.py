import pytest


from app.agent.multi.graph import (
    create_multi_agent_graph,
)

class FakeLLM:


    def with_structured_output(
        self,
        schema,
    ):

        return self


    async def ainvoke(
        self,
        prompt,
    ):

        return type(
            "Route",
            (),
            {
                "agent":
                "order",

                "reason":
                "订单退款"
            }
        )()

@pytest.mark.asyncio
async def test_order_handoff_ticket():
    graph = create_multi_agent_graph(
        FakeLLM()
    )


    result = await graph.ainvoke(

        {

            "question":
            "订单一直没到，我想退款",


            "next_agent":
            None,


            "answer":
            None,


            "history":
            [],


            "route_reason":
            None,


            "handoff_to":
            None,

        }

    )


    assert (
        result["answer"]
        ==
        "已经创建工单"
    )

