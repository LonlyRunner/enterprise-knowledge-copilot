"""MCP client public API.

The repository contains both the historical ``app/mcp/client.py`` module and
this package. Python resolves the package first, so the public classes must be
exported here to keep existing imports working.
"""
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPClient:
    def __init__(self, session: ClientSession):
        self.session = session

    async def list_tools(self):
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: dict):
        return await self.session.call_tool(name, arguments)


class HTTPMCPClient:
    def __init__(self, url: str):
        self.url = url
        self._transport = None
        self._transport_context = None
        self.session: ClientSession | None = None

    async def connect(self):
        self._transport_context = streamable_http_client(self.url)
        # Recent MCP SDK versions return a third callback containing the
        # stream session id.  The client only needs the read/write streams,
        # so keep compatibility with both the 2- and 3-value APIs.
        result = await self._transport_context.__aenter__()
        read, write = result[:2]
        self._transport = (read, write)
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        return self

    async def close(self):
        if self.session is not None:
            await self.session.__aexit__(None, None, None)
            self.session = None
        if self._transport_context is not None:
            await self._transport_context.__aexit__(None, None, None)
            self._transport_context = None

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
