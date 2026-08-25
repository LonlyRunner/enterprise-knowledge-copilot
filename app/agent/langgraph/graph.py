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
)


from app.agent.langgraph.agents import (
    OrderAgentNode,
    RagAgentNode,
)



def create_customer_graph(
    order_agent,
    rag_agent,
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