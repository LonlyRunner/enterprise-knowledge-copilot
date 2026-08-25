"""Mock order-system APIs used by Agent and frontend integration exercises."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.business_gateway import MockBusinessGateway

router = APIRouter(prefix="/orders", tags=["Orders"])
gateway = MockBusinessGateway()


class TicketRequest(BaseModel):
    reason: str = Field(min_length=2, max_length=500)
    approved: bool = False
    tenant_id: str = "default"
    user_id: str = "demo-user"


@router.get("")
async def list_orders(
    tenant_id: str = Query("default", min_length=1, max_length=100),
    user_id: str = Query("demo-user", min_length=1, max_length=100),
    status: str | None = Query(None, max_length=40),
    query: str | None = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=100),
):
    orders = await gateway.list_orders(
        tenant_id=tenant_id,
        user_id=user_id,
        status=status,
        query=query,
        limit=limit,
    )
    return {"items": orders, "total": len(orders), "tenant_id": tenant_id, "user_id": user_id}


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    tenant_id: str = Query("default"),
    user_id: str = Query("demo-user"),
):
    result = await gateway.query_order(order_id, tenant_id=tenant_id, user_id=user_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="订单不存在")
    return result["data"]


@router.get("/{order_id}/logistics")
async def get_logistics(
    order_id: str,
    tenant_id: str = Query("default"),
    user_id: str = Query("demo-user"),
):
    result = await gateway.query_logistics(order_id, tenant_id=tenant_id, user_id=user_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    return result["data"]


@router.post("/{order_id}/tickets")
async def create_ticket(order_id: str, request: TicketRequest):
    if not request.approved:
        return {
            "success": False,
            "requires_approval": True,
            "message": "创建售后工单属于写操作，需要人工审批",
        }
    return await gateway.create_ticket(
        order_id,
        request.reason,
        tenant_id=request.tenant_id,
        user_id=request.user_id,
    )
