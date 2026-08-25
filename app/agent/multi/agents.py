class OrderAgent:


    async def run(
        self,
        state,
    ):


        state["answer"] = (
            "订单正在运输"
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


        state["answer"] = (
            "已经创建工单"
        )


        return state