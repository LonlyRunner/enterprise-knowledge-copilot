from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.business_gateway import MockBusinessGateway


class EnterpriseMCPService:
    """In-process MCP boundary used locally and by the HTTP MCP server."""

    def __init__(self, gateway: MockBusinessGateway | None = None):
        self.gateway = gateway or MockBusinessGateway(enforce_identity=True)
        self._profiles = {
            "demo-user": {
                "customer_id": "CUST-1001",
                "name": "张晨",
                "level": "enterprise",
                "region": "华东",
            },
            "finance-user": {
                "customer_id": "CUST-2001",
                "name": "星河制造（上海）有限公司",
                "level": "strategic",
                "region": "华东",
            },
        }

    def list_capabilities(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "tools": [
                {"name": "list_orders", "description": "按当前租户和用户查询订单列表", "side_effect": False},
                {"name": "query_order", "description": "查询订单详情", "side_effect": False},
                {"name": "query_logistics", "description": "查询订单物流", "side_effect": False},
                {"name": "create_ticket", "description": "创建售后工单，需要审批", "side_effect": True, "requires_approval": True},
            ],
            "resources": [
                {"uri": "customer://profile/{user_id}", "name": "customer_profile"},
                {"uri": "order://history/{user_id}", "name": "order_history"},
                {"uri": "policy://company/customer-service", "name": "company_policy"},
            ],
            "prompts": [
                {"name": "customer_service_agent_prompt", "description": "企业客服 Agent 统一提示模板"},
            ],
        }

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        tenant_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        if name == "list_orders":
            items = await self.gateway.list_orders(
                tenant_id=tenant_id,
                user_id=user_id,
                status=arguments.get("status"),
                query=arguments.get("query"),
                limit=int(arguments.get("limit", 100)),
            )
            return {"success": True, "data": {"items": items, "total": len(items)}}
        if name == "query_order":
            return await self.gateway.query_order(
                arguments["order_id"], tenant_id=tenant_id, user_id=user_id
            )
        if name == "query_logistics":
            return await self.gateway.query_logistics(
                arguments["order_id"], tenant_id=tenant_id, user_id=user_id
            )
        if name == "create_ticket":
            if not arguments.get("approved", False):
                return {
                    "success": False,
                    "requires_approval": True,
                    "error_code": "APPROVAL_REQUIRED",
                }
            return await self.gateway.create_ticket(
                arguments["order_id"],
                arguments["reason"],
                tenant_id=tenant_id,
                user_id=user_id,
            )
        return {"success": False, "error_code": "TOOL_NOT_FOUND", "tool": name}

    async def read_resource(
        self,
        uri: str,
        *,
        tenant_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        if uri.startswith("customer://profile/"):
            requested_user = uri.rsplit("/", 1)[-1]
            if requested_user != user_id:
                return {"success": False, "error_code": "RESOURCE_FORBIDDEN"}
            return {"success": True, "data": self._profiles.get(user_id, {"name": user_id, "level": "standard"})}
        if uri.startswith("order://history/"):
            requested_user = uri.rsplit("/", 1)[-1]
            if requested_user != user_id:
                return {"success": False, "error_code": "RESOURCE_FORBIDDEN"}
            orders = await self.gateway.list_orders(tenant_id=tenant_id, user_id=user_id, limit=100)
            return {"success": True, "data": {"items": orders, "total": len(orders)}}
        if uri == "policy://company/customer-service":
            path = Path(__file__).resolve().parents[2] / "data" / "customer_service_sla.md"
            return {"success": True, "data": {"content": path.read_text(encoding="utf-8")}}
        return {"success": False, "error_code": "RESOURCE_NOT_FOUND"}

    async def get_prompt(self, name: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        if name != "customer_service_agent_prompt":
            return {"success": False, "error_code": "PROMPT_NOT_FOUND"}
        variables = variables or {}
        return {
            "success": True,
            "data": {
                "name": name,
                "template": (
                    "你是星云科技企业客服 Action Agent。只执行已授权的工具；"
                    "查询结果必须说明来源；创建工单、退款和审批等写操作必须先获得人工批准。"
                ),
                "variables": variables,
            },
        }
