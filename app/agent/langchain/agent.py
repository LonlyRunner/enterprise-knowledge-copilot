from langchain.agents import create_agent

from app.agent.langchain.mcp_adapter import mcp_tool_to_langchain_tool


def create_langchain_agent(
    llm,
    tools,
):
    """
    LangChain 1.x 基础Agent
    """

    return create_agent(

        model=llm,

        tools=tools,

        system_prompt=(
            "你是企业智能客服助手，"
            "根据工具结果回答用户问题。"
        ),
    )



def create_conversation_agent(
    llm,
    tools,
):
    """
    带Conversation能力的Agent

    当前只是基础包装，
    Memory由ConversationAgent处理。
    """

    return create_langchain_agent(
        llm,
        tools,
    )


async def load_mcp_tools(
    mcp_client,
):


    tools = []


    schemas = await (
        mcp_client.list_tools()
    )


    for schema in schemas:

        tools.append(

            mcp_tool_to_langchain_tool(
                mcp_client,
                schema,
            )

        )


    return tools