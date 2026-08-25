from langchain_core.tools import (
    StructuredTool,
)



def create_langchain_tool_from_mcp(
    client,
    schema,
):


    async def invoke(
        **kwargs,
    ):


        result = await (
            client.call_tool(
                schema.name,
                kwargs,
            )
        )


        return result



    return StructuredTool.from_function(

        coroutine=invoke,

        name=schema.name,

        description=(
            schema.description
        ),
    )