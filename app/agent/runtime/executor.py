class AgentExecutor:


    def __init__(
        self,
        graph,
    ):

        self.graph = graph



    async def run(
        self,
        input,
        config,
    ):


        result = await (
            self.graph
            .ainvoke(
                input,
                config=config,
            )
        )


        return result