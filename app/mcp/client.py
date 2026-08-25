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