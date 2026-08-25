from app.tools.order import QueryOrderTool
from app.services.business_gateway import MockBusinessGateway

# 创建单例工具实例。BusinessGateway 是协议，不能直接实例化；本地 MCP
# 适配器使用与企业联调页面相同的文件型 Mock 网关。
_gateway = MockBusinessGateway()
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
