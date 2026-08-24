from app.agent.agent import ReactAgent


def FakeRagTool():
    pass


async def test_agent_tool_call():


    agent=ReactAgent(
        tools=[
            FakeRagTool()
        ]
    )


    result=await agent.run(
        "查询报销规则"
    )


    assert result