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
    order_node,
    knowledge_node,
)



def create_customer_graph():


    graph = StateGraph(
        AgentState
    )


    graph.add_node(
        "router",
        intent_router,
    )


    graph.add_node(
        "order",
        order_node,
    )


    graph.add_node(
        "knowledge",
        knowledge_node,
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
        END,
    )


    graph.add_edge(
        "knowledge",
        END,
    )


    return graph.compile()