import pytest


from app.tools.registry import (
    create_tool_registry,
)

from app.tools.executor import (
    DefaultToolExecutor,
)

from app.services.business_gateway import (
    MockBusinessGateway,
)



@pytest.mark.asyncio
async def test_execute_query_order():


    gateway = MockBusinessGateway()

    registry = create_tool_registry(
        gateway
    )

    executor = DefaultToolExecutor(
        registry,
        gateway,
    )


    result = await executor.execute(
        "query_order",
        {
            "order_id":
            "XN-2026-000381"
        },
        tenant_id="tenant001",
        user_id="user001",
        trace_id="trace001",
    )


    assert result["success"] is True



@pytest.mark.asyncio
async def test_execute_unknown_tool():
    gateway = MockBusinessGateway()

    registry = create_tool_registry(
        gateway
    )



    executor = DefaultToolExecutor(
        registry,
        gateway,
    )


    result = await executor.execute(
        "unknown_tool",
        {},
        tenant_id="tenant001",
        user_id="user001",
        trace_id="trace001",
    )


    assert (
        result["error_code"]
        == "TOOL_NOT_FOUND"
    )