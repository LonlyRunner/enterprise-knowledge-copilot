from app.agent.runtime.executor import (
    AgentExecutor,
)


from app.agent.multi.graph import (
    create_multi_agent_graph,
)



async def create_agent():



    graph = (
        create_multi_agent_graph()
    )


    return AgentExecutor(
        graph
    )