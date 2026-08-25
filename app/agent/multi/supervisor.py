from app.agent.multi.state import (
    MultiAgentState,
)



async def supervisor_node(
    state,
    router,
):


    result = await (
        router.route(
            state["question"]
        )
    )


    state["next_agent"] = (
        result.agent
    )


    state["route_reason"] = (
        result.reason
    )


    return state