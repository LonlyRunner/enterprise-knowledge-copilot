class LLMEvaluator:


    def __init__(
        self,
        llm_client,
    ):

        self.llm_client=llm_client



    async def evaluate(
        self,
        *,
        question,
        answer,
        context,
    ):


        prompt=f"""

评价下面回答：

问题:
{question}


知识:
{context}


回答:
{answer}


返回JSON:

{{
"faithfulness":0-1,
"relevance":0-1
}}

"""


        result=await self.llm_client.chat(
            prompt
        )


        return result