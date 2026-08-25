from langchain_core.tools import StructuredTool


def convert_to_langchain_tool(
    tool,
):
    """
    企业Tool转换成LangChain Tool
    """

    async def execute(
        **kwargs
    ):

        return await tool.execute(
            kwargs,

            tenant_id="system",

            user_id="system",

            trace_id="langchain",
        )


    return StructuredTool.from_function(
        coroutine=execute,

        name=tool.definition.name,

        description=(
            tool.definition.description
        ),
    )