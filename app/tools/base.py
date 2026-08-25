from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ToolDefinition:
    """
    Agent工具定义

    给LLM看的能力描述
    """

    name: str

    description: str

    input_schema: dict[str, Any]

    side_effect: bool = False

    requires_approval: bool = False


class ToolExecutor(Protocol):
    """
    工具执行协议

    真正执行逻辑由后续 BusinessGateway 实现
    """

    async def execute(
        self,
        arguments: dict[str, Any],
        *,
        tenant_id: str,
        user_id: str,
        trace_id: str,
    ) -> dict[str, Any]:
        ...


class ToolRegistry:
    """
    工具注册中心

    Agent通过这里发现工具
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        tool: ToolDefinition,
    ):
        self._tools[tool.name] = tool


    def get(
        self,
        name: str,
    ) -> ToolDefinition | None:
        return self._tools.get(name)


    def schemas(self) -> list[dict[str, Any]]:
        """
        转换成OpenAI兼容tool schema
        """

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in self._tools.values()
        ]