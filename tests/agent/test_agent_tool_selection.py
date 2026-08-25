import pytest


class FakeToolCallingLLM:


    def __init__(self):

        self.calls = []


    async def ainvoke(
        self,
        messages,
    ):

        content = (
            messages[-1]
            .content
        )


        if "退款" in content:


            self.calls.append(
                "knowledge_search"
            )


            return {

                "tool":
                "knowledge_search",

                "arguments":
                {
                    "question":
                    content
                }
            }


        if "订单" in content:


            self.calls.append(
                "query_order"
            )


            return {

                "tool":
                "query_order",

                "arguments":
                {
                    "order_id":
                    "XN-2026-000381"
                }
            }


        return {

            "answer":
            "无法判断"
        }



@pytest.mark.asyncio
async def test_agent_choose_rag_tool():


    llm = FakeToolCallingLLM()


    result = await llm.ainvoke(
        [
            type(
                "Message",
                (),
                {
                    "content":
                    "公司的退款政策是什么？"
                }
            )()
        ]
    )


    assert (
        result["tool"]
        ==
        "knowledge_search"
    )



@pytest.mark.asyncio
async def test_agent_choose_order_tool():


    llm = FakeToolCallingLLM()


    result = await llm.ainvoke(
        [
            type(
                "Message",
                (),
                {
                    "content":
                    "我的订单在哪里？"
                }
            )()
        ]
    )


    assert (
        result["tool"]
        ==
        "query_order"
    )