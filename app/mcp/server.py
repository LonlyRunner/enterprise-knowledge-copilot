from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    "customer-service"
)


@mcp.tool()
async def query_order(
    order_id: str,
):

    """
    查询订单状态
    """


    return {

        "order_id":
        order_id,

        "status":
        "运输中"

    }



if __name__ == "__main__":

    mcp.run()