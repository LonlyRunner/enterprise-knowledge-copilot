"""Mock order-system APIs used by Agent and frontend integration exercises."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.rbac import require_permission
from app.db.dependencies import get_db
from app.services.approval_service import ApprovalService
from app.services.business_gateway import MockBusinessGateway

router = APIRouter(prefix="/orders", tags=["Orders"])
gateway = MockBusinessGateway(enforce_identity=True)


class TicketRequest(BaseModel):
    reason: str = Field(min_length=2, max_length=500)
    # Kept for backwards-compatible clients; server-side ApprovalService is authoritative.
    approved: bool = False
    approval_id: str | None = Field(default=None, min_length=1, max_length=80)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)


@router.get("")
async def list_orders(
    status: str | None = Query(None, max_length=40),
    query: str | None = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_permission("order:read")),
):
    orders = await gateway.list_orders(tenant_id=user.tenant_id, user_id="demo-user" if user.id == "anonymous" else str(user.id), status=status, query=query, limit=limit)
    return {"items": orders, "total": len(orders), "tenant_id": user.tenant_id, "user_id": user.id}


@router.get("/{order_id}")
async def get_order(order_id: str, user: User = Depends(require_permission("order:read"))):
    user_id = "demo-user" if user.id == "anonymous" else str(user.id)
    result = await gateway.query_order(order_id, tenant_id=user.tenant_id, user_id=user_id)
    if not result["success"] or result["data"].get("tenant_id") != user.tenant_id or (result["data"].get("user_id") not in {user_id, "demo-user" if user.id == "anonymous" else user_id}):
        raise HTTPException(status_code=404, detail="订单不存在")
    return result["data"]


@router.get("/{order_id}/logistics")
async def get_logistics(order_id: str, user: User = Depends(require_permission("order:read"))):
    user_id = "demo-user" if user.id == "anonymous" else str(user.id)
    result = await gateway.query_logistics(order_id, tenant_id=user.tenant_id, user_id=user_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    order = await gateway.query_order(order_id, tenant_id=user.tenant_id, user_id=user_id)
    if not order.get("success") or order["data"].get("tenant_id") != user.tenant_id or order["data"].get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    return result["data"]


@router.post("/{order_id}/tickets")
async def create_ticket(order_id: str, request: TicketRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_permission("order:write"))):
    user_id = "demo-user" if user.id == "anonymous" else str(user.id)
    order = await gateway.query_order(order_id, tenant_id=user.tenant_id, user_id=user_id)
    if not order.get("success") or order["data"].get("tenant_id") != user.tenant_id or order["data"].get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="订单不存在")
    if not request.approved:
        approval_id = request.approval_id or f"approval-{uuid.uuid4().hex[:12]}"
        approval = await ApprovalService(db).create_pending(approval_id=approval_id, tenant_id=user.tenant_id, user_id=user_id, action="create_ticket", payload={"order_id": order_id, "reason": request.reason}, idempotency_key=request.idempotency_key)
        await db.commit()
        return {"success": False, "requires_approval": True, "approval_id": approval.approval_id, "message": "创建售后工单属于写操作，需要人工审批"}
    if not request.approval_id:
        raise HTTPException(status_code=400, detail="approval_id is required")
    await ApprovalService(db).approve_many([request.approval_id], tenant_id=user.tenant_id, user_id=user_id)
    result = await gateway.create_ticket(order_id, request.reason, tenant_id=user.tenant_id, user_id=user_id)
    await db.commit()
    return result
