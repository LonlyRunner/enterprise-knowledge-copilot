from mcp import ClientSession


class MCPConnection:


    def __init__(
        self,
        session: ClientSession,
    ):

        self.session = session



    async def initialize(
        self,
    ):

        await (
            self.session
            .initialize()
        )



    async def list_tools(
        self,
    ):

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


        return await (
            self.session
            .call_tool(
                name,
                arguments,
            )
        )