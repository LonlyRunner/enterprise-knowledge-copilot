from app.tools.base import ToolDefinition


class KnowledgeSearchTool:
    """
    企业知识库查询工具

    包装已有 RAG Service
    """

    definition = ToolDefinition(

        name="knowledge_search",

        description=(
            "查询企业政策、售后规则、"
            "产品说明等知识。"
        ),

        input_schema={

            "type":"object",

            "properties":{

                "question":{

                    "type":"string",

                    "description":
                    "用户问题",
                }
            },

            "required":[
                "question"
            ],

            "additionalProperties":
            False,
        },

        side_effect=False,

        requires_approval=False,
    )


    def __init__(
        self,
        rag_service,
    ):
        self.rag_service = rag_service



    async def execute(
        self,
        arguments: dict,
        *,
        tenant_id: str,
        user_id: str,
        trace_id: str,
    ):

        question = arguments.get(
            "question"
        )


        if not question:

            return {
                "success":False,
                "error_code":
                "INVALID_ARGUMENT",
            }


        result = await self.rag_service.query(
            question=question,
            tenant_id=tenant_id,
        )


        return {
            "success":True,
            "data":result,
        }