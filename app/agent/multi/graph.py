from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from redisvl.extensions.cache import llm

from app.agent.multi.router import SupervisorRouter
from app.agent.multi.state import (
    MultiAgentState,
)


from app.agent.multi.supervisor import (
    supervisor_node,
)


from app.agent.multi.agents import (
    OrderAgent,
    RagAgent,
    TicketAgent,
)



def create_multi_agent_graph():


    graph = StateGraph(
        MultiAgentState
    )


    order = OrderAgent()

    rag = RagAgent()

    ticket = TicketAgent()



    graph.add_node(
        "supervisor",
        supervisor_node,
    )


    graph.add_node(
        "order",
        order.run,
    )


    graph.add_node(
        "rag",
        rag.run,
    )


    graph.add_node(
        "ticket",
        ticket.run,
    )

    router = SupervisorRouter(
        llm
    )

    graph.add_node(

        "supervisor",

        lambda state:
        supervisor_node(
            state,
            router,
        )

    )



    graph.add_conditional_edges(

        "supervisor",

        lambda state:
        state["next_agent"],

        {

            "order":
            "order",

            "rag":
            "rag",

            "ticket":
            "ticket",

        }
    )


    graph.add_edge(
        "order",
        END,
    )


    graph.add_edge(
        "rag",
        END,
    )


    graph.add_edge(
        "ticket",
        END,
    )


    return graph.compile()