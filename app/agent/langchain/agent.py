from langchain.agents import (
    create_tool_calling_agent,
    AgentExecutor,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)


def create_langchain_agent(
    llm,
    tools,
):
    """
    创建 LangChain Tool Calling Agent
    """


    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是企业智能客服助手，"
                "根据工具结果回答用户问题。",
            ),

            (
                "human",
                "{input}",
            ),

            MessagesPlaceholder(
                variable_name="agent_scratchpad"
            ),
        ]
    )


    agent = create_tool_calling_agent(
        llm,
        tools,
        prompt,
    )


    executor = AgentExecutor(
        agent=agent,

        tools=tools,

        verbose=True,

        max_iterations=5,
    )


    return executor