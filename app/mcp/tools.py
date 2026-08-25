from app.tools.order import QueryOrderTool
from app.services.business_gateway import BusinessGateway

# 创建单例工具实例
_gateway = BusinessGateway()
_query_order_tool = QueryOrderTool(gateway=_gateway)

async def query_order_tool(order_id: str, tenant_id: str = "default", user_id: str = "default"):
    """
    查询订单的工具函数（包装类的方法）
    """
    result = await _query_order_tool.execute(
        arguments={"order_id": order_id},
        tenant_id=tenant_id,
        user_id=user_id,
        trace_id="mcp_trace"  # 可以生成唯一 trace_id
    )
    return result