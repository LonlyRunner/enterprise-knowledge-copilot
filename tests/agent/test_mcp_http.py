import pytest

from app.mcp.client import HTTPMCPClient


@pytest.mark.asyncio
async def test_http_mcp_connect():


    client = await (
        HTTPMCPClient(
            "http://localhost:8001/mcp"
        )
        .connect()
    )


    tools = await (
        client.session.list_tools()
    )


    assert len(
        tools.tools
    ) > 0