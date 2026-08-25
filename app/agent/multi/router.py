from app.agent.multi.models import (
    AgentRoute,
)



class SupervisorRouter:


    def __init__(
        self,
        llm,
    ):

        self.llm = llm



    async def route(
        self,
        question: str,
    ) -> AgentRoute:


        prompt = f"""
你是客服系统路由器。

根据用户问题选择 Agent。

可选：

order:
订单、物流、配送

rag:
政策、规则、说明

ticket:
投诉、售后、人工


用户问题:

{question}


只输出JSON。
"""


        result = await (
            self.llm
            .with_structured_output(
                AgentRoute
            )
            .ainvoke(
                prompt
            )
        )


        return result