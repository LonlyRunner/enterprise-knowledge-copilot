import pytest

from dataclasses import dataclass


from app.tools.registry import (
    create_tool_registry,
)

from app.tools.executor import (
    DefaultToolExecutor,
)

from app.services.business_gateway import (
    MockBusinessGateway,
)


from app.agent.agent import (
    NativeAgent,
)



@dataclass
class FakeToolCall:

    id: str

    name: str

    arguments: dict



@dataclass
class FakeLLMResponse:

    content: str | None = None

    tool_calls: list | None = None



class FakeLLM:

    """
    模拟模型行为

    第一次:
    调用 query_order

    第二次:
    根据工具结果回答
    """

    def __init__(self):

        self.count = 0



    async def chat_with_tools(
        self,
        messages,
        tools,
    ):


        self.count += 1


        if self.count == 1:

            return FakeLLMResponse(

                content=None,

                tool_calls=[

                    FakeToolCall(

                        id="call_001",

                        name="query_order",

                        arguments={

                            "order_id":
                            "XN-2026-000381"
                        },
                    )
                ],
            )


        return FakeLLMResponse(

            content=
            "您的订单正在运输中，预计送达。",

            tool_calls=[],
        )



@pytest.fixture
def agent():


    gateway = MockBusinessGateway()


    registry = create_tool_registry(
        gateway
    )


    executor = DefaultToolExecutor(
        registry
    )


    return NativeAgent(

        llm=FakeLLM(),

        executor=executor,

        registry=registry,

        max_steps=5,
    )



@pytest.mark.asyncio
async def test_native_agent_tool_call_flow(
    agent,
):


    result = await agent.run(

        "我的订单XN-2026-000381什么时候到?",

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace001",
    )


    assert (
        result["answer"]
        ==
        "您的订单正在运输中，预计送达。"
    )


    assert (
        result["steps"]
        ==
        2
    )



@pytest.mark.asyncio
async def test_native_agent_without_tool(
    agent,
):


    result = await agent.run(

        "你好",

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace002",
    )


    assert (
        "answer"
        in result
    )