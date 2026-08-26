from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import ApprovalModel


class ApprovalService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pending(self, *, approval_id: str, tenant_id: str, user_id: str, action: str, payload: dict, idempotency_key: str | None = None, ttl_seconds: int = 900) -> ApprovalModel:
        existing_by_id = await self.session.scalar(select(ApprovalModel).where(ApprovalModel.approval_id == approval_id, ApprovalModel.tenant_id == tenant_id, ApprovalModel.user_id == user_id))
        if existing_by_id:
            return existing_by_id
        if idempotency_key:
            existing = await self.session.scalar(select(ApprovalModel).where(ApprovalModel.tenant_id == tenant_id, ApprovalModel.user_id == user_id, ApprovalModel.idempotency_key == idempotency_key))
            if existing:
                return existing
        model = ApprovalModel(approval_id=approval_id, tenant_id=tenant_id, user_id=user_id, action=action, payload=payload, idempotency_key=idempotency_key, expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds))
        self.session.add(model)
        await self.session.flush()
        return model

    async def approve_many(self, approval_ids: list[str], *, tenant_id: str, user_id: str) -> None:
        if not approval_ids:
            raise ValueError("approval_ids are required for write actions")
        now = datetime.now(UTC)
        for approval_id in approval_ids:
            model = await self.session.scalar(select(ApprovalModel).where(ApprovalModel.approval_id == approval_id, ApprovalModel.tenant_id == tenant_id, ApprovalModel.user_id == user_id))
            if model is None or model.status != "pending" or model.expires_at <= now:
                raise ValueError(f"approval is invalid or expired: {approval_id}")
            model.status = "approved"
            model.approved_by = user_id
            model.approved_at = now
        await self.session.flush()

    async def claim_many(self, approval_ids: list[str], *, tenant_id: str, user_id: str) -> None:
        """Atomically move approved records to executing before side effects."""
        if not approval_ids:
            raise ValueError("approval_ids are required for execution")
        for approval_id in approval_ids:
            model = await self.session.scalar(
                select(ApprovalModel).where(
                    ApprovalModel.approval_id == approval_id,
                    ApprovalModel.tenant_id == tenant_id,
                    ApprovalModel.user_id == user_id,
                )
            )
            if model is None or model.status != "approved":
                raise ValueError(f"approval is not ready for execution: {approval_id}")
            model.status = "executing"
        await self.session.flush()

    async def finalize_many(self, approval_ids: list[str], *, tenant_id: str, user_id: str, success: bool) -> None:
        """Consume successful approvals and make failed actions explicitly retryable/auditable."""
        if not approval_ids:
            return
        final_status = "consumed" if success else "failed"
        for approval_id in approval_ids:
            model = await self.session.scalar(
                select(ApprovalModel).where(
                    ApprovalModel.approval_id == approval_id,
                    ApprovalModel.tenant_id == tenant_id,
                    ApprovalModel.user_id == user_id,
                )
            )
            if model is not None and model.status == "executing":
                model.status = final_status
        await self.session.flush()
