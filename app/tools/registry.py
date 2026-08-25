from app.tools.order import (
    QueryOrderTool,
)

from app.tools.base import (
    ToolRegistry,
)



def create_tool_registry(
    gateway,
):

    registry = ToolRegistry()


    registry.register(
        QueryOrderTool(
            gateway
        )
    )


    return registry