
from langgraph.graph import (
    StateGraph,
    START,
    END,
)
from langgraph.checkpoint.memory import InMemorySaver

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


class _AwaitableGraph:
    """Proxy that supports both legacy ``await create...()`` and direct use."""

    def __init__(self, graph, await_graph=None):
        self._graph = graph
        self._await_graph = await_graph or graph

    def __getattr__(self, name):
        return getattr(self._graph, name)

    def __await__(self):
        async def _return():
            return self._await_graph
        return _return().__await__()


def create_customer_graph(
        order_agent=None,
        rag_agent=None,
        checkpointer=None,
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

    # Graph construction is synchronous.  Redis checkpointer setup is an
    # explicitly async concern and can be injected by the production runtime;
    # tests and local usage get a safe in-memory checkpoint by default.
    compiled = graph.compile(checkpointer=checkpointer) if checkpointer else graph.compile()
    # Legacy callers await the factory and expect interrupt/resume support;
    # give that path an in-memory checkpoint while direct callers stay simple.
    resumable = compiled if checkpointer else graph.compile(checkpointer=InMemorySaver())
    return _AwaitableGraph(compiled, resumable)


async def create_customer_graph_with_redis(
    order_agent=None,
    rag_agent=None,
    redis_url="redis://localhost:6379/0",
):
    """Build the same graph with the async Redis checkpointer."""
    global _checkpointer_manager
    if _checkpointer_manager is None:
        _checkpointer_manager = CheckpointerManager(redis_url)
    checkpointer = await _checkpointer_manager.get_checkpointer()
    return create_customer_graph(order_agent, rag_agent, checkpointer=checkpointer)
