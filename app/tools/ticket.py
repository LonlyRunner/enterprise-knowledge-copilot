from app.tools.base import ToolDefinition


class CreateTicketTool:

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