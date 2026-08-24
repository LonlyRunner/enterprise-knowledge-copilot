from typing import Protocol



class Tool(Protocol):


    name:str


    description:str


    async def execute(
        self,
        input:str,
    ):
        ...

    class RagTool:
        name = "knowledge_search"

        description = """
        查询企业知识库
        """

        def __init__(
                self,
                rag_service,
        ):
            self.rag_service = rag_service

        async def execute(
                self,
                input: str,
        ):
            result = await (
                self.rag_service.chat(
                    question=input
                )
            )

            return result