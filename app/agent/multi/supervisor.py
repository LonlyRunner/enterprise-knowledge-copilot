from app.agent.multi.state import (
    MultiAgentState,
)



async def supervisor_node(
    state: MultiAgentState,
):


    question = (
        state["question"]
    )


    if "订单" in question:

        state["next_agent"] = (
            "order"
        )


    elif (
        "退款" in question
        or "政策" in question
    ):

        state["next_agent"] = (
            "rag"
        )


    else:

        state["next_agent"] = (
            "ticket"
        )


    return state