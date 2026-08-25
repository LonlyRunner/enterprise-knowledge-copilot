from app.agent.langgraph.state import (
    AgentState,
)
from langgraph.types import interrupt


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


async def refund_check_node(
    state,
):


    amount = 800


    if amount > 500:

        state["need_human_review"] = True


        decision = interrupt(
            {
                "type":
                "refund_review",

                "amount":
                amount,

                "message":
                "退款金额超过自动审批额度"
            }
        )


        state["human_action"] = (
            decision
        )


    return state