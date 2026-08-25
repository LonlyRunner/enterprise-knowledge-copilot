from app.tools.base import ToolDefinition

from app.services.business_gateway import (
    BusinessGateway,
)


class QueryLogisticsTool:
    """
    查询物流状态
    """

    definition = ToolDefinition(

        name="query_logistics",

        description=(
            "查询订单物流状态和预计送达时间。"
            "只能查询，不执行物流修改。"
        ),

        input_schema={

            "type": "object",

            "properties": {

                "order_id": {

                    "type": "string",

                    "pattern":
                    "^XN-[0-9]{4}-[0-9]{6}$",

                    "description":
                    "订单编号",
                }
            },

            "required": [
                "order_id"
            ],

            "additionalProperties":
            False,
        },

        side_effect=False,

        requires_approval=False,
    )


    def __init__(
        self,
        gateway: BusinessGateway,
    ):
        self.gateway = gateway



    async def execute(
        self,
        arguments: dict,
        *,
        tenant_id: str,
        user_id: str,
        trace_id: str,
    ):

        order_id = arguments.get(
            "order_id"
        )


        if not order_id:
            return {
                "success": False,
                "error_code":
                "INVALID_ARGUMENT",
            }


        return await self.gateway.query_logistics(
            order_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )