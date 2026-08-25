from app.tools.base import ToolRegistry
from app.tools.order import query_order_tool


def create_tool_registry() -> ToolRegistry:
    """
    创建 Agent 工具注册中心

    后续新增工具：
    query_logistics
    knowledge_search
    create_ticket

    都在这里注册
    """

    registry = ToolRegistry()

    registry.register(
        query_order_tool
    )

    return registry