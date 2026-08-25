import pytest


from langchain_core.messages import (
    AIMessage,
)


from langchain_core.language_models import (
    BaseChatModel,
)


from langchain_core.outputs import (
    ChatGeneration,
    ChatResult,
)
from pydantic import Field

from app.agent.langchain.adapters import (
    convert_to_langchain_tool,
)


from app.agent.langchain.agent import (
    create_langchain_agent,
)


from app.tools.registry import (
    create_tool_registry,
)


from app.services.business_gateway import (
    MockBusinessGateway,
)


from typing import ClassVar


class FakeLangChainChatModel(
    BaseChatModel
):
    call_count: ClassVar[int] = 0

    tools: list = Field(
        default_factory=list
    )

    @property
    def _llm_type(self):

        return "fake"

    def _generate(
            self,
            messages,
            stop=None,
            run_manager=None,
            **kwargs,
    ):

        FakeLangChainChatModel.call_count += 1

        if FakeLangChainChatModel.call_count == 1:

            message = AIMessage(

                content="",

                tool_calls=[

                    {
                        "name":
                            "query_order",

                        "args":
                            {
                                "order_id":
                                    "XN-2026-000381"
                            },

                        "id":
                            "call_001",
                    }
                ],
            )


        else:

            message = AIMessage(

                content=
                "您的订单正在运输中。",
            )

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=message
                )
            ]
        )

    def bind_tools(
            self,
            tools,
            **kwargs,
    ):

        return self.model_copy(
            update={
                "tools": tools
            }
        )



@pytest.mark.asyncio
async def test_langchain_agent_tool_call():


    registry = create_tool_registry(
        MockBusinessGateway()
    )


    enterprise_tool = registry.get(
        "query_order"
    )


    lc_tool = convert_to_langchain_tool(
        enterprise_tool
    )


    llm = FakeLangChainChatModel()


    executor = create_langchain_agent(
        llm,
        [
            lc_tool
        ]
    )

    result = await executor.ainvoke(
        {
            "messages": [
                {
                    "role":
                        "user",

                    "content":
                        "我的订单什么时候到?"
                }
            ]
        }
    )


    assert (
        "订单"
        in result["messages"][-1].content
    )


@pytest.mark.asyncio
async def test_langchain_agent_tool_call():

    FakeLangChainChatModel.call_count = 0