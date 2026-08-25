from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "customer-service",
    host="127.0.0.1",
    port=8001,
)

@mcp.tool()
async def query_order(order_id: str):
    """
    查询订单状态
    """
    return {
        "success": True,
        "data": {
            "order_id": order_id,
            "status": "运输中",
            "customer": "张三",
            "created_at": "2026-08-25 10:00:00"
        }
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")