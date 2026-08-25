from app.agent.agent import (
    NativeAgent,
)


class OrderAgentNode:
    """
    订单 Agent Node
    """


    def __init__(
        self,
        agent: NativeAgent,
    ):

        self.agent = agent


    async def run(
        self,
        state,
    ):


        result = await self.agent.run(

            state["question"],

            tenant_id=(
                state["tenant_id"]
            ),

            user_id=(
                state["user_id"]
            ),

            trace_id=(
                state["trace_id"]
            ),
        )


        state["answer"] = (
            result["answer"]
        )


        return state



class RagAgentNode:
    """
    知识库 Agent Node
    """


    def __init__(
        self,
        rag_agent,
    ):

        self.rag_agent = rag_agent



    async def run(
        self,
        state,
    ):


        result = await (
            self.rag_agent.run(
                state["question"]
            )
        )


        state["answer"] = result
        state["usage"] = result.get(
            "usage",
            {}
        )


        return state