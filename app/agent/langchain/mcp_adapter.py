from langchain_core.tools import (
    StructuredTool,
)


def mcp_tool_to_langchain_tool(
    mcp_client,
    tool_schema,
):


    async def execute(
        **kwargs,
    ):

        result = await (
            mcp_client.call_tool(
                tool_schema.name,
                kwargs,
            )
        )

        return result



    return StructuredTool.from_function(
        coroutine=execute,

        name=(
            tool_schema.name
        ),

        description=(
            tool_schema.description
        ),
    )