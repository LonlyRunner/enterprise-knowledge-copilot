from app.tools.base import ToolDefinition


query_order_tool = ToolDefinition(
    name="query_order",

    description=(
        "查询当前登录客户有权限访问的订单状态。"
        "只能查询订单信息，不执行修改操作。"
    ),

    input_schema={
        "type": "object",

        "properties": {
            "order_id": {
                "type": "string",

                "pattern": "^XN-[0-9]{4}-[0-9]{6}$",

                "description": (
                    "星云科技订单号，例如 XN-2026-000381"
                ),
            }
        },

        "required": [
            "order_id"
        ],

        "additionalProperties": False,
    },

    side_effect=False,

    requires_approval=False,
)