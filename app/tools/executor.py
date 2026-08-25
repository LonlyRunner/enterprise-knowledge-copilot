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
        arguments: dict[str, Any],
        *,
        tenant_id: str,
        user_id: str,
        trace_id: str,
    ) -> dict[str, Any]:

        tool = self.registry.get(
            tool_name
        )


        if tool is None:
            return {
                "success": False,
                "error_code": "TOOL_NOT_FOUND",
            }


        if tool_name == "query_order":

            order_id = arguments.get(
                "order_id"
            )


            if not order_id:
                return {
                    "success": False,
                    "error_code": "INVALID_ARGUMENT",
                }


            return await self.business_gateway.query_order(
                order_id,
                tenant_id=tenant_id,
                user_id=user_id,
            )


        return {
            "success": False,
            "error_code": "UNSUPPORTED_TOOL",
        }