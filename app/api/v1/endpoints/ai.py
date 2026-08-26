import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.db.dependencies import get_db
from app.gateway.limiter import RateLimitExceeded
from app.gateway.schemas import GatewayRequest, GatewayResponse
from app.gateway.service import AIGatewayService
from app.utils.sse import encode_sse

router = APIRouter(prefix="/ai", tags=["AI Gateway"])
service = AIGatewayService()
logger = logging.getLogger(__name__)


def _context(user: User) -> tuple[str, str]:
    # The local mock dataset uses demo-user while authenticated production
    # users use their persisted id.
    user_id = "demo-user" if user.id == "anonymous" else str(user.id)
    return user.tenant_id, user_id


async def _run(request: GatewayRequest, db: AsyncSession, user: User, *, delta_callback: Callable[[str], Awaitable[None]] | None = None) -> GatewayResponse:
    tenant_id, user_id = _context(user)
    try:
        result = await service.handle(
            request,
            session=db,
            tenant_id=tenant_id,
            user_id=user_id,
            delta_callback=delta_callback,
        )
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail={"code": "RATE_LIMITED", "retry_after": exc.retry_after_seconds},
        ) from exc
    # AgentResult and GatewayResponse intentionally share the same contract,
    # but Pydantic does not coerce a sibling model instance directly.
    return GatewayResponse.model_validate(result.model_dump(mode="json"))


@router.post("/chat", response_model=GatewayResponse)
async def ai_chat(
    request: GatewayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _run(request, db, user)


@router.post("/agent", response_model=GatewayResponse)
async def ai_agent(
    request: GatewayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request = request.model_copy(update={"mode": "agent"})
    return await _run(request, db, user)


@router.post("/stream")
async def ai_stream(
    request: GatewayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    http_request: Request = None,
):
    async def events() -> AsyncIterator[str]:
        yield encode_sse("start", {})
        queue: asyncio.Queue[str] = asyncio.Queue()
        async def on_delta(delta: str) -> None:
            await queue.put(delta)
        task = None
        try:
            task = asyncio.create_task(_run(request, db, user, delta_callback=on_delta))
            while not task.done() or not queue.empty():
                if http_request is not None and await http_request.is_disconnected():
                    task.cancel()
                    return
                try:
                    delta = await asyncio.wait_for(queue.get(), timeout=0.25)
                    yield encode_sse("delta", {"content": delta})
                except asyncio.TimeoutError:
                    continue
            result = await task
            for step in result.agent_steps:
                yield encode_sse("step", step.model_dump(mode="json"))
            yield encode_sse("result", result.model_dump(mode="json"))
            yield encode_sse("done", {})
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("AI stream failed")
            yield encode_sse("error", {"message": "AI request failed", "code": "AI_STREAM_ERROR"})
        finally:
            if task is not None and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
