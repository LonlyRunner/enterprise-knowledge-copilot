from app.tools.base import (
    BaseTool,
    ToolDefinition,
)


class KnowledgeSearchTool(
    BaseTool
):
    """
    企业知识库搜索 Tool
    """


    def __init__(
        self,
        rag_service,
    ):

        self.rag_service = (
            rag_service
        )


    @property
    def definition(
        self,
    ):

        return ToolDefinition(

            name=
            "knowledge_search",

            description=
            (
                "查询企业知识库，"
                "适用于政策、"
                "流程、"
                "产品说明等问题"
            ),

            parameters={

                "type":
                "object",

                "properties":{

                    "question":{

                        "type":
                        "string",

                        "description":
                        "用户问题"

                    }

                },

                "required":[
                    "question"
                ]
            }
        )



    async def execute(
        self,
        arguments,
        *,
        tenant_id,
        user_id,
        trace_id,
    ):


        result = await (
            self.rag_service.chat(
                question=
                arguments["question"],

                user_id=
                user_id,
            )
        )


        return {

            "success":
            True,

            "answer":
            result,

        }