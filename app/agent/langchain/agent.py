from langchain.agents import create_agent


def create_langchain_agent(
    llm,
    tools,
):
    """
    LangChain 1.x Agent

    基于 create_agent
    """


    agent = create_agent(

        model=llm,

        tools=tools,

        system_prompt=(
            "你是企业智能客服助手，"
            "根据工具结果回答用户问题。"
        ),
    )


    return agent