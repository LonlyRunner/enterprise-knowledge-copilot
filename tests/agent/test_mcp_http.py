import pytest
import socket

from app.mcp.client import HTTPMCPClient


def _mcp_server_available() -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", 8001)) == 0


pytestmark = pytest.mark.skipif(
    not _mcp_server_available(),
    reason="MCP HTTP integration server is not running on localhost:8001",
)


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
