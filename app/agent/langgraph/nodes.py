from app.agent.langgraph.state import (
    AgentState,
)


async def intent_router(
    state: AgentState,
):


    question = (
        state["question"]
    )


    if "订单" in question:

        state["intent"] = (
            "order"
        )


    else:

        state["intent"] = (
            "knowledge"
        )


    return state



async def order_node(
    state: AgentState,
):


    state["answer"] = (
        "订单正在运输中"
    )


    return state



async def knowledge_node(
    state: AgentState,
):


    state["answer"] = (
        "根据知识库查询结果"
    )


    return state