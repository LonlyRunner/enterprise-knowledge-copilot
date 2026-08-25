"""Business-system boundary used by Agent tools and local order integration UI."""
from __future__ import annotations

import copy
import json
import uuid
from pathlib import Path
from typing import Protocol


class BusinessGateway(Protocol):
    async def query_order(self, order_id: str, *, tenant_id: str, user_id: str) -> dict:
        ...


class MockBusinessGateway:
    """File-backed mock implementation that mirrors a real order service."""

    def __init__(self, data_path: str | Path | None = None):
        path = Path(data_path) if data_path else Path(__file__).resolve().parents[2] / "data" / "order_mock_data.json"
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            records = [
                {"order_id": "XN-2026-000381", "status": "shipping", "status_label": "运输中", "product": "AI服务器", "amount": 8999, "tenant_id": "default", "user_id": "demo-user", "logistics": []},
                {"order_id": "XN-2026-000382", "status": "completed", "status_label": "已完成", "product": "企业软件授权", "amount": 19999, "tenant_id": "default", "user_id": "demo-user", "logistics": []},
            ]
        self.orders: dict[str, dict] = {item["order_id"]: item for item in records}
        self.tickets: list[dict] = []

    async def list_orders(
        self,
        *,
        tenant_id: str = "default",
        user_id: str = "demo-user",
        status: str | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        result = []
        for order in self.orders.values():
            # A real gateway would enforce identity in the downstream service.
            # The mock keeps the two demo identities visible for easy UI testing.
            visible = order.get("tenant_id") == tenant_id and (
                order.get("user_id") == user_id
                or (user_id == "default" and order.get("user_id") == "demo-user")
            )
            if not visible:
                continue
            if status and order.get("status") != status:
                continue
            if query and query.lower() not in f"{order.get('order_id', '')} {order.get('product', '')}".lower():
                continue
            result.append(copy.deepcopy(order))
        return result[: max(1, min(limit, 100))]

    async def query_order(self, order_id: str, *, tenant_id: str, user_id: str) -> dict:
        order = self.orders.get(order_id)
        if order is None:
            return {"success": False, "error_code": "ORDER_NOT_FOUND"}
        return {"success": True, "data": copy.deepcopy(order)}

    async def query_logistics(self, order_id: str, *, tenant_id: str, user_id: str) -> dict:
        order = self.orders.get(order_id)
        if order is None:
            return {"success": False, "error_code": "LOGISTICS_NOT_FOUND"}
        return {
            "success": True,
            "data": {
                "order_id": order_id,
                "status": order.get("status_label", order.get("status")),
                "carrier": order.get("carrier"),
                "tracking_no": order.get("tracking_no"),
                "eta": order.get("eta"),
                "events": copy.deepcopy(order.get("logistics", [])),
            },
        }

    async def create_ticket(self, order_id: str, reason: str, *, tenant_id: str, user_id: str) -> dict:
        if order_id not in self.orders:
            return {"success": False, "error_code": "ORDER_NOT_FOUND"}
        ticket = {
            "ticket_id": f"TK-{uuid.uuid4().hex[:10].upper()}",
            "order_id": order_id,
            "reason": reason,
            "status": "pending_review",
            "status_label": "待人工审核",
            "tenant_id": tenant_id,
            "user_id": user_id,
        }
        self.tickets.append(ticket)
        return {"success": True, "data": copy.deepcopy(ticket)}
