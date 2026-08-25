import pytest


from app.mcp.client import (
    MCPClient,
)



class FakeSession:


    async def list_tools(
        self,
    ):

        class Result:

            tools = [

                type(
                    "Tool",
                    (),
                    {
                        "name":
                        "query_order",

                        "description":
                        "查询订单"
                    }
                )()

            ]


        return Result()



    async def call_tool(
        self,
        name,
        arguments,
    ):

        return {

            "name":
            name,

            "arguments":
            arguments
        }



@pytest.mark.asyncio
async def test_mcp_client():


    client = MCPClient(
        FakeSession()
    )


    tools = await (
        client.list_tools()
    )


    assert (
        tools[0].name
        ==
        "query_order"
    )


    result = await (
        client.call_tool(
            "query_order",

            {
                "order_id":
                "XN-001"
            }
        )
    )


    assert (
        result["name"]
        ==
        "query_order"
    )