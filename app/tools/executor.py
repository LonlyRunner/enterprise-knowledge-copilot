from typing import Any

from app.tools.base import ToolRegistry


class DefaultToolExecutor:
    """
    通用工具执行器

    职责：

    1. 根据 tool_name 找 Tool
    2. 调用 Tool.execute()
    3. 返回结构化结果

    不包含业务判断
    """


    def __init__(
        self,
        registry: ToolRegistry,
    ):

        self.registry = registry



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
                "error_code":
                "TOOL_NOT_FOUND",
            }


        try:

            result = await tool.execute(
                arguments,

                tenant_id=tenant_id,

                user_id=user_id,

                trace_id=trace_id,
            )


            return result


        except Exception as exc:

            return {

                "success": False,

                "error_code":
                "TOOL_EXECUTION_ERROR",

                "message":
                str(exc),
            }