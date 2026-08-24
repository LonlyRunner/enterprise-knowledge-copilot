class AgentRouter:



    async def route(
        self,
        question,
    ):


        if (
            "分析"
            in question
        ):

            return "agent"


        return "rag"