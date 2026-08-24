class ReactAgent:


    def __init__(
        self,
        llm_client,
        tools,
    ):

        self.llm_client=llm_client

        self.tools={
            tool.name:tool
            for tool in tools
        }



    async def run(
        self,
        question:str,
    ):


        state=[]


        while True:


            decision=await (
                self.llm_client.chat(
                    question
                )
            )


            if decision.type=="tool":


                tool=(
                    self.tools[
                        decision.tool_name
                    ]
                )


                result=await (
                    tool.execute(
                        decision.input
                    )
                )


                state.append(
                    result
                )


            else:

                return decision.answer