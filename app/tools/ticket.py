from app.services.business_gateway import BusinessGateway
from app.tools.base import ToolDefinition


class CreateTicketTool:

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
        order_id = arguments.get("order_id")
        reason = arguments.get("reason")

        if not order_id or not reason:
            return {
                "success": False,
                "error_code": "INVALID_ARGUMENT",
            }

        return await self.gateway.create_ticket(
            order_id,
            reason,
            tenant_id=tenant_id,
            user_id=user_id,
        )

    definition = ToolDefinition(

        name="create_ticket",

        description=(
            "创建售后工单。"
            "属于业务写操作，需要审批。"
        ),

        input_schema={

            "type":"object",

            "properties":{

                "order_id":{

                    "type":"string"
                },

                "reason":{

                    "type":"string"
                }
            },

            "required":[
                "order_id",
                "reason",
            ],

            "additionalProperties":
            False,
        },


        side_effect=True,

        requires_approval=True,



    )
