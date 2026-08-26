from __future__ import annotations

import re
import uuid
from typing import Any

from app.contracts import AgentArtifact, ApprovalRequest, ToolInvocation
from app.gateway.schemas import GatewayRequest
from app.mcp.enterprise import EnterpriseMCPService


class ProjectCActionAgent:
    def __init__(self, mcp: EnterpriseMCPService | None = None):
        self.mcp = mcp or EnterpriseMCPService()
        self._tool_calls: list[ToolInvocation] = []

    async def run(self, request: GatewayRequest, action: str, *, tenant_id: str, user_id: str) -> dict[str, Any]:
        self._tool_calls = []
        if action == "analyze_sales":
            return await self._analyze_sales(request, tenant_id=tenant_id, user_id=user_id)
        order_id = self._find_order_id(request.question)
        if not order_id:
            orders = await self._call("list_orders", {}, tenant_id=tenant_id, user_id=user_id)
            return {
                "status": "completed" if orders.get("success") else "failed",
                "summary": "未识别到订单号，已返回可用订单列表",
                "data": orders,
                "tool_calls": self._calls,
                "approvals": [],
                "artifacts": [],
            }

        if action == "query_logistics":
            order = await self._call("query_order", {"order_id": order_id}, tenant_id=tenant_id, user_id=user_id)
            logistics = await self._call("query_logistics", {"order_id": order_id}, tenant_id=tenant_id, user_id=user_id)
            return {
                "status": "completed" if order.get("success") and logistics.get("success") else "partial",
                "summary": f"已查询订单 {order_id} 的订单和物流",
                "data": {"order": order, "logistics": logistics},
                "tool_calls": self._calls,
                "approvals": [],
                "artifacts": [],
            }

        order = await self._call("query_order", {"order_id": order_id}, tenant_id=tenant_id, user_id=user_id)
        if not order.get("success"):
            return {
                "status": "failed",
                "summary": f"订单 {order_id} 查询失败",
                "data": {"order": order},
                "tool_calls": self._calls,
                "approvals": [],
                "artifacts": [],
            }
        approvals: list[ApprovalRequest] = []
        if action == "handle_ticket" or "创建工单" in request.question:
            reason = "用户请求售后处理"
            approval_id = f"approval-{uuid.uuid4().hex[:12]}"
            if not request.approve_actions:
                approvals.append(
                    ApprovalRequest(
                        approval_id=approval_id,
                        action="create_ticket",
                        reason=reason,
                        payload={"order_id": order_id, "reason": reason},
                    )
                )
                return {
                    "status": "pending_approval",
                    "summary": f"订单 {order_id} 查询完成，创建工单需要人工审批",
                    "data": {"order": order},
                    "tool_calls": self._calls,
                    "approvals": approvals,
                    "artifacts": [],
                }
            ticket = await self._call(
                "create_ticket",
                {"order_id": order_id, "reason": reason, "approved": True},
                tenant_id=tenant_id,
                user_id=user_id,
            )
            approvals.append(
                ApprovalRequest(
                    approval_id=approval_id,
                    action="create_ticket",
                    reason=reason,
                    payload={"order_id": order_id},
                    status="approved",
                )
            )
            return {
                "status": "completed",
                "summary": f"订单 {order_id} 查询完成并已创建售后工单",
                "data": {"order": order, "ticket": ticket},
                "tool_calls": self._calls,
                "approvals": approvals,
                "artifacts": [],
            }
        return {
            "status": "completed",
            "summary": f"已查询订单 {order_id}",
            "data": {"order": order},
            "tool_calls": self._calls,
            "approvals": [],
            "artifacts": [],
        }

    async def _analyze_sales(self, request: GatewayRequest, *, tenant_id: str, user_id: str) -> dict[str, Any]:
        result = await self._call("list_orders", {}, tenant_id=tenant_id, user_id=user_id)
        items = (result.get("data") or {}).get("items", [])
        total = sum(float(item.get("amount", 0)) for item in items)
        anomalies = [
            item for item in items
            if item.get("status") in {"pending_payment", "refunding"}
        ]
        report = {
            "order_count": len(items),
            "total_amount": total,
            "currency": "CNY",
            "status_counts": self._status_counts(items),
            "anomaly_orders": anomalies,
        }
        artifacts = [
            AgentArtifact(
                type="report",
                name="sales-summary.json",
                content=report,
            )
        ]
        approvals = []
        ticket_results = []
        if anomalies and ("工单" in request.question or "异常" in request.question):
            for item in anomalies[:5]:
                order_id = item["order_id"]
                reason = f"异常订单自动识别：{item.get('status_label', item.get('status'))}"
                approval_id = f"approval-{uuid.uuid4().hex[:12]}"
                if request.approve_actions:
                    ticket_results.append(
                        await self._call(
                            "create_ticket",
                            {"order_id": order_id, "reason": reason, "approved": True},
                            tenant_id=tenant_id,
                            user_id=user_id,
                        )
                    )
                else:
                    approvals.append(
                        ApprovalRequest(
                            approval_id=approval_id,
                            action="create_ticket",
                            reason=reason,
                            payload={"order_id": order_id, "reason": reason},
                        )
                    )
        if ticket_results:
            report["created_tickets"] = ticket_results
        return {
            "status": "completed" if request.approve_actions or not approvals else "pending_approval",
            "summary": f"分析 {len(items)} 个订单，识别 {len(anomalies)} 个异常订单",
            "data": report,
            "tool_calls": self._calls,
            "approvals": approvals,
            "artifacts": artifacts,
        }

    async def _call(self, name: str, arguments: dict[str, Any], *, tenant_id: str, user_id: str) -> dict[str, Any]:
        result = await self.mcp.call_tool(name, arguments, tenant_id=tenant_id, user_id=user_id)
        self._calls.append(
            ToolInvocation(
                tool=name,
                arguments=arguments,
                success=bool(result.get("success")),
                result=result,
            )
        )
        return result

    @property
    def _calls(self) -> list[ToolInvocation]:
        return self._tool_calls

    @staticmethod
    def _find_order_id(question: str) -> str | None:
        match = re.search(r"XN-\d{4}-\d{6}", question)
        return match.group(0) if match else None

    @staticmethod
    def _status_counts(items: list[dict]) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in items:
            status = item.get("status_label") or item.get("status") or "unknown"
            result[status] = result.get(status, 0) + 1
        return result
