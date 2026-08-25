import pytest


from app.mcp.server import (
    query_order,
)



@pytest.mark.asyncio
async def test_mcp_query_order():


    result = await query_order(
        "XN-001"
    )


    assert result is not None