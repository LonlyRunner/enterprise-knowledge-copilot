from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.agent.multi.handoff import handoff_router
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



def create_multi_agent_graph(
    llm=None,
):


    graph = StateGraph(
        MultiAgentState
    )


    order = OrderAgent()

    rag = RagAgent()

    ticket = TicketAgent()


    if llm is None:
        class _DeterministicRouter:
            async def route(self, question: str):
                if any(word in question for word in ("投诉", "售后", "人工")):
                    agent, reason = "ticket", "售后或人工服务"
                elif any(word in question for word in ("订单", "物流", "配送", "退款")):
                    agent, reason = "order", "订单或物流问题"
                else:
                    agent, reason = "rag", "知识库问题"
                return type("Route", (), {"agent": agent, "reason": reason})()

        router = _DeterministicRouter()
    else:
        router = SupervisorRouter(llm)


    async def supervisor_wrapper(
        state,
    ):

        return await supervisor_node(
            state,
            router,
        )


    # ===== Nodes =====


    graph.add_node(
        "supervisor",
        supervisor_wrapper,
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



    # ===== Entry =====


    graph.add_edge(
        START,
        "supervisor",
    )



    # ===== Supervisor Routing =====


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



    # ===== Handoff =====


    graph.add_conditional_edges(

        "order",

        handoff_router,

        {

            "ticket":
            "ticket",

            "end":
            END,

        }

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
