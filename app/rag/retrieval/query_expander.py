class QueryExpander:


    def __init__(
        self,
        llm_client,
    ):

        self.llm_client=llm_client



    async def expand(
        self,
        query:str,
    ):


        prompt=f"""

生成三个相关搜索问题：

{query}

只返回列表。

"""


        result=await (
            self.llm_client.chat(
                prompt
            )
        )


        return result