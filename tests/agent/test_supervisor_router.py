import pytest


from app.agent.multi.router import (
    SupervisorRouter,
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
            "AgentRoute",
            (),
            {
                "agent":
                "order",

                "reason":
                "查询订单"
            }
        )()



@pytest.mark.asyncio
async def test_router():


    router = SupervisorRouter(
        FakeLLM()
    )


    result = await (
        router.route(
            "我的订单在哪里"
        )
    )


    assert (
        result.agent
        ==
        "order"
    )