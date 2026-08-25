import pytest

from dataclasses import dataclass


from app.agent.agent import (
    NativeAgent,
)


from app.tools.registry import (
    create_tool_registry,
)


from app.tools.executor import (
    DefaultToolExecutor,
)


from app.services.business_gateway import (
    MockBusinessGateway,
)



@dataclass
class FakeToolCall:

    id: str

    name: str

    arguments: dict



@dataclass
class FakeLLMResponse:

    role: str = "assistant"

    content: str | None = None

    tool_calls: list | None = None



class MultiToolFakeLLM:


    def __init__(self):

        self.step = 0



    async def chat_with_tools(
        self,
        messages,
        tools,
    ):


        self.step += 1


        # 第一次查询订单

        if self.step == 1:

            return FakeLLMResponse(

                tool_calls=[

                    FakeToolCall(

                        id="call_order",

                        name="query_order",

                        arguments={

                            "order_id":
                            "XN-2026-000381"
                        }
                    )
                ]
            )


        # 第二次查询物流

        if self.step == 2:

            return FakeLLMResponse(

                tool_calls=[

                    FakeToolCall(

                        id="call_logistics",

                        name="query_logistics",

                        arguments={

                            "order_id":
                            "XN-2026-000381"
                        }
                    )
                ]
            )


        return FakeLLMResponse(

            content=
            "您的订单正在运输中，预计2026-08-28送达。"
        )



@pytest.mark.asyncio
async def test_multi_tool_call():


    gateway = MockBusinessGateway()


    registry = create_tool_registry(
        gateway
    )


    executor = DefaultToolExecutor(
        registry
    )


    agent = NativeAgent(

        llm=MultiToolFakeLLM(),

        executor=executor,

        registry=registry,

        max_steps=5,
    )


    result = await agent.run(

        "我的订单什么时候到？",

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace001",
    )


    assert (
        result["answer"]
        ==
        "您的订单正在运输中，预计2026-08-28送达。"
    )


    assert (
        result["steps"]
        ==
        3
    )



class InfiniteFakeLLM:


    async def chat_with_tools(
        self,
        messages,
        tools,
    ):

        return FakeLLMResponse(

            tool_calls=[

                FakeToolCall(

                    id="loop",

                    name="query_order",

                    arguments={

                        "order_id":
                        "XN-2026-000381"
                    }
                )
            ]
        )



@pytest.mark.asyncio
async def test_max_steps_protection():


    gateway = MockBusinessGateway()


    registry = create_tool_registry(
        gateway
    )


    executor = DefaultToolExecutor(
        registry
    )


    agent = NativeAgent(

        llm=InfiniteFakeLLM(),

        executor=executor,

        registry=registry,

        max_steps=3,
    )


    result = await agent.run(

        "查询订单",

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace002",
    )


    assert (
        result["steps"]
        ==
        3
    )


    assert (
        result["answer"]
        ==
        "超过最大执行步骤"
    )



class ErrorGateway:

    async def query_order(
        self,
        *args,
        **kwargs,
    ):

        raise Exception(
            "database error"
        )



@pytest.mark.asyncio
async def test_tool_exception_handling():


    registry = create_tool_registry(
        ErrorGateway()
    )


    executor = DefaultToolExecutor(
        registry
    )


    result = await executor.execute(

        "query_order",

        {
            "order_id":
            "XN-2026-000381"
        },

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace003",
    )


    assert (
        result["success"]
        is False
    )


    assert (
        result["error_code"]
        ==
        "TOOL_EXECUTION_ERROR"
    )