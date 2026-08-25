from typing import Any

from app.tools.base import ToolRegistry
from app.services.business_gateway import (
    BusinessGateway,
)


class DefaultToolExecutor:
    """
    默认工具执行器

    负责：
    - 找工具
    - 参数检查
    - 调用业务服务
    - 返回结构化结果
    """

    def __init__(
        self,
        registry: ToolRegistry,
        business_gateway: BusinessGateway,
    ):
        self.registry = registry
        self.business_gateway = business_gateway

    async def execute(
            self,
            tool_name: str,
            arguments: dict,
            *,
            tenant_id: str,
            user_id: str,
            trace_id: str,
    ):
        tool = self.registry.get(
            tool_name
        )

        if tool is None:
            return {
                "success": False,
                "error_code":
                    "TOOL_NOT_FOUND",
            }

        return await tool.execute(
            arguments,
            tenant_id=tenant_id,
            user_id=user_id,
            trace_id=trace_id,
        )