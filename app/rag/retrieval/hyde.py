class HyDERetriever:


    def __init__(
        self,
        llm_client,
    ):

        self.llm_client=llm_client



    async def generate_document(
        self,
        question,
    ):


        prompt=f"""

生成一个可能回答：

{question}

"""


        return await (
            self.llm_client.chat(
                prompt
            )
        )