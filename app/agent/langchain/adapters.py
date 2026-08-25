from langchain_core.tools import StructuredTool


def convert_to_langchain_tool(
    tool,
):
    """
    企业Tool -> LangChain StructuredTool

    保留原有:
    - ToolDefinition
    - execute()
    """

    async def async_execute(
        **kwargs,
    ):

        return await tool.execute(
            kwargs,

            tenant_id="langchain",

            user_id="system",

            trace_id="langchain-adapter",
        )


    return StructuredTool.from_function(
        coroutine=async_execute,

        name=(
            tool.definition.name
        ),

        description=(
            tool.definition.description
        ),
    )