
from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agent.langgraph.state import (
    AgentState,
)


from app.agent.langgraph.nodes import (
    intent_router,
    refund_check_node,
)


from app.agent.langgraph.agents import (
    OrderAgentNode,
    RagAgentNode,
)


from app.agent.langgraph.checkpointer import (
    CheckpointerManager,
)


id="c2q9zq"
_checkpointer_manager = None


async def create_customer_graph(
        order_agent=None,
        rag_agent=None,

):





    order_agent_node = (
        OrderAgentNode(
            order_agent
        )
    )


    rag_agent_node = (
        RagAgentNode(
            rag_agent
        )
    )


    graph = StateGraph(
        AgentState
    )


    graph.add_node(
        "router",
        intent_router,
    )


    graph.add_node(
        "order",
        order_agent_node.run,
    )


    graph.add_node(
        "knowledge",
        rag_agent_node.run,
    )


    graph.add_node(
        "refund_check",
        refund_check_node,
    )


    graph.add_edge(
        START,
        "router",
    )


    graph.add_conditional_edges(

        "router",

        lambda state:
        state["intent"],

        {

            "order":
            "order",

            "knowledge":
            "knowledge",

        }

    )


    graph.add_edge(
        "order",
        "refund_check",
    )


    def check_human(state):

        if state.get(
            "need_human_review",
            False
        ):

            return "human"


        return "end"


    graph.add_conditional_edges(

        "refund_check",

        check_human,

        {

            "human":
            END,

            "end":
            END,

        }

    )


    graph.add_edge(
        "knowledge",
        END,
    )

    global _checkpointer_manager

    if _checkpointer_manager is None:
        _checkpointer_manager = (
            CheckpointerManager(
                "redis://localhost:6379/0"
            )
        )

    checkpointer = await (
        _checkpointer_manager
        .get_checkpointer()
    )

    return graph.compile(
        checkpointer=checkpointer
    )