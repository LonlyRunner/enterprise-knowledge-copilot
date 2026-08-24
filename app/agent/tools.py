from typing import Protocol


class Tool(Protocol):
    name: str
    description: str

    async def execute(self, input: str):
        ...


class RagTool:
    name = "knowledge_search"
    description = "查询企业知识库"

    def __init__(self, rag_service, *, knowledge_base_id, conversation_id):
        self.rag_service = rag_service
        self.knowledge_base_id = knowledge_base_id
        self.conversation_id = conversation_id

    async def execute(self, input: str):
        return await self.rag_service.chat(
            knowledge_base_id=self.knowledge_base_id,
            conversation_id=self.conversation_id,
            question=input,
        )
