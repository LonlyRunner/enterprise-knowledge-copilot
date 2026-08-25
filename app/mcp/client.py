from mcp import ClientSession

from mcp.client.streamable_http import (
    streamablehttp_client,
)


from mcp import ClientSession
class MCPClient:


    def __init__(
        self,
        session: ClientSession,
    ):

        self.session = session



    async def list_tools(self):

        result = await (
            self.session
            .list_tools()
        )


        return result.tools



    async def call_tool(
        self,
        name: str,
        arguments: dict,
    ):


        result = await (
            self.session
            .call_tool(
                name,
                arguments,
            )
        )


        return result

class HTTPMCPClient:


    def __init__(
        self,
        url:str,
    ):

        self.url=url



    async def connect(
        self,
    ):


        self.transport = (
            streamablehttp_client(
                self.url
            )
        )


        read, write, _ = (
            await self.transport.__aenter__()
        )


        self.session = (
            ClientSession(
                read,
                write,
            )
        )


        await (
            self.session.initialize()
        )


        return self