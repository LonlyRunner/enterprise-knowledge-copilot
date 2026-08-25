from app.core.observability.tracer import (
    AgentTracer,
)



class OrderAgent:


    async def run(
        self,
        state,
    ):

        tracer = AgentTracer()


        tracer.start(
            "order_agent"
        )


        question = (
            state["question"]
        )


        if "退款" in question:

            state["handoff_to"] = (
                "ticket"
            )


        else:

            state["answer"] = (
                "订单正在运输"
            )


        tracer.end(
            "order_agent"
        )


        return state


class RagAgent:


    async def run(
        self,
        state,
    ):


        state["answer"] = (
            "根据知识库回答"
        )


        return state


class TicketAgent:


    async def run(
        self,
        state,
    ):


        print(
            "Ticket Agent running"
        )


        state["answer"] = (
            "已经创建工单"
        )


        return state
