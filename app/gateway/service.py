from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from prometheus_client import Counter, Histogram
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.project_c import ProjectCOrchestrator
from app.agent.project_c.chat_agent import ProjectCChatAgent
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.contracts import AgentResult
from app.gateway.audit import GatewayAuditLogger
from app.gateway.limiter import RedisRateLimiter
from app.gateway.schemas import GatewayRequest
from app.llm.client import create_llm_client
from app.rag.context import TokenCounter
from app.services.approval_service import ApprovalService

GATEWAY_REQUESTS = Counter(
    "ai_gateway_requests_total",
    "AI Gateway requests",
    ["mode", "status"],
)
GATEWAY_LATENCY = Histogram(
    "ai_gateway_request_duration_seconds",
    "AI Gateway latency",
    ["mode"],
)


class AIGatewayService:
    def __init__(
        self,
        *,
        limiter: RedisRateLimiter | None = None,
        audit: GatewayAuditLogger | None = None,
        orchestrator_factory=ProjectCOrchestrator,
    ):
        self.settings = get_settings()
        self.limiter = limiter or RedisRateLimiter()
        self.audit = audit or GatewayAuditLogger()
        self.orchestrator_factory = orchestrator_factory

    async def handle(
        self,
        request: GatewayRequest,
        *,
        session: AsyncSession,
        tenant_id: str,
        user_id: str,
        request_id: str | None = None,
        task_id: str | None = None,
        trace_id: str | None = None,
        delta_callback: Callable[[str], Awaitable[None]] | None = None,
    ) -> AgentResult:
        import time

        request_id = request_id or f"req-{uuid.uuid4().hex[:12]}"
        task_id = task_id or f"task-{uuid.uuid4().hex[:12]}"
        trace_id = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
        started = time.perf_counter()
        mode = request.mode
        await self.limiter.check(
            f"{tenant_id}:{user_id}",
            limit=self.settings.gateway_rate_limit_per_minute,
        )
        await self.audit.write(
            "gateway.request.accepted",
            trace_id=trace_id,
            tenant_id=tenant_id,
            user_id=user_id,
            payload={"request_id": request_id, "task_id": task_id, "mode": mode, "question_length": len(request.question)},
        )

        llm = None
        executable_approval_ids: list[str] = []
        try:
            selected_model = request.model or self.settings.gateway_default_model
            if selected_model not in {self.settings.deepseek_model, "project-c-router"}:
                raise AppException("Unsupported model", code="MODEL_NOT_SUPPORTED", status_code=400)
            if selected_model == self.settings.deepseek_model:
                llm = create_llm_client()
            approval_ids = [str(item) for item in request.metadata.get("approval_ids", [])]
            execution_request = request
            if request.approve_actions and session is not None:
                if approval_ids:
                    try:
                        await ApprovalService(session).approve_many(approval_ids, tenant_id=tenant_id, user_id=user_id)
                        await ApprovalService(session).claim_many(approval_ids, tenant_id=tenant_id, user_id=user_id)
                        executable_approval_ids = approval_ids
                    except ValueError as exc:
                        raise AppException(str(exc), code="APPROVAL_INVALID", status_code=403) from exc
                else:
                    # First pass only plans and returns server-persisted approvals.
                    execution_request = request.model_copy(update={"approve_actions": False})

            orchestrator = self.orchestrator_factory(
                chat_agent=ProjectCChatAgent(llm),
                token_counter=TokenCounter().count_text,
                model=selected_model,
            )
            result = await orchestrator.run(
                execution_request,
                session=session,
                request_id=request_id,
                task_id=task_id,
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                delta_callback=delta_callback,
            )
            if session is not None and result.approvals:
                approval_service = ApprovalService(session)
                for approval in result.approvals:
                    if approval.status == "pending":
                        await approval_service.create_pending(
                            approval_id=approval.approval_id,
                            tenant_id=tenant_id,
                            user_id=user_id,
                            action=approval.action,
                            payload=approval.payload,
                            idempotency_key=request.metadata.get("idempotency_key"),
                        )
                await session.commit()
            if session is not None and executable_approval_ids:
                await ApprovalService(session).finalize_many(
                    executable_approval_ids,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    success=result.status == "completed",
                )
                await session.commit()
            result.route = mode
            GATEWAY_REQUESTS.labels(mode, result.status).inc()
            await self.audit.write(
                "gateway.request.completed",
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                payload={
                    "request_id": request_id,
                    "task_id": task_id,
                    "status": result.status,
                    "route": result.route,
                    "tool_count": len(result.tool_calls),
                    "approval_count": len(result.approvals),
                    "total_tokens": result.usage.total_tokens,
                },
            )
            return result
        except AppException:
            if session is not None and executable_approval_ids:
                await ApprovalService(session).finalize_many(executable_approval_ids, tenant_id=tenant_id, user_id=user_id, success=False)
                await session.commit()
            GATEWAY_REQUESTS.labels(mode, "failed").inc()
            raise
        except Exception as exc:
            if session is not None and executable_approval_ids:
                await ApprovalService(session).finalize_many(executable_approval_ids, tenant_id=tenant_id, user_id=user_id, success=False)
                await session.commit()
            GATEWAY_REQUESTS.labels(mode, "failed").inc()
            await self.audit.write(
                "gateway.request.failed",
                trace_id=trace_id,
                tenant_id=tenant_id,
                user_id=user_id,
                payload={"request_id": request_id, "error_type": type(exc).__name__},
            )
            raise AppException("AI Gateway request failed", code="GATEWAY_ERROR", status_code=502) from exc
        finally:
            GATEWAY_LATENCY.labels(mode).observe(time.perf_counter() - started)
            if llm is not None:
                await llm.close()


class GatewayService:
    """Project-B compatibility facade used by existing unit tests/callers."""

    async def execute(self, request) -> AgentResult:
        from app.agent.project_c.chat_agent import ProjectCChatAgent
        from app.agent.project_c.orchestrator import ProjectCOrchestrator
        from app.gateway.schemas import GatewayRequest

        legacy = GatewayRequest(
            question=getattr(request, "question", None) or getattr(request, "message", None),
            mode="chat",
        )
        return await ProjectCOrchestrator(
            chat_agent=ProjectCChatAgent(),
        ).run(
            legacy,
            session=None,
            request_id=f"req-{uuid.uuid4().hex[:12]}",
            task_id=f"task-{uuid.uuid4().hex[:12]}",
            trace_id=f"trace-{uuid.uuid4().hex[:12]}",
            tenant_id="default",
            user_id="demo-user",
        )
