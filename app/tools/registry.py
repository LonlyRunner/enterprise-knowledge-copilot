from app.tools.order import (
    QueryOrderTool,
)

from app.tools.base import (
    ToolRegistry,
)


from app.tools.logistics import (
    QueryLogisticsTool,
)

from app.tools.rag import (
    KnowledgeSearchTool,
)

from app.tools.ticket import (
    CreateTicketTool,
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

    registry.register(
        QueryLogisticsTool(gateway)
    )

    registry.register(
        CreateTicketTool()
    )


    return registry