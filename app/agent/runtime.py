from app.agent.agent import NativeAgent

from app.agent.langgraph.graph import (
    create_customer_graph,
)

from app.agent.factory import (
    create_native_agent,
)



def create_agent_graph():


    native_agent = (
        create_native_agent()
    )


    return create_customer_graph(

        order_agent=native_agent,

        rag_agent=None,

    )