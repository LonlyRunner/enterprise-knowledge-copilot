from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.project_c.action_agent import ProjectCActionAgent
from app.agent.project_c.chat_agent import ProjectCChatAgent
from app.agent.project_c.rag_agent import ProjectCRagAgent
from app.agent.project_c.supervisor import SupervisorAgent
from app.contracts import AgentResult, AgentStep, TokenUsageSummary
from app.gateway.schemas import GatewayRequest


class ProjectCOrchestrator:
    def __init__(
        self,
        *,
        supervisor: SupervisorAgent | None = None,
        rag_agent: ProjectCRagAgent | None = None,
        action_agent: ProjectCActionAgent | None = None,
        chat_agent: ProjectCChatAgent | None = None,
        token_counter: Callable[[str], int] | None = None,
        model: str = "project-c-router",
    ):
        self.supervisor = supervisor or SupervisorAgent()
        self.rag_agent = rag_agent or ProjectCRagAgent()
        self.action_agent = action_agent or ProjectCActionAgent()
        self.chat_agent = chat_agent or ProjectCChatAgent()
        self.token_counter = token_counter or (lambda text: max(1, len(text) // 2))
        self.model = model

    async def run(
        self,
        request: GatewayRequest,
        *,
        session: AsyncSession,
        request_id: str,
        task_id: str,
        trace_id: str,
        tenant_id: str,
        user_id: str,
        delta_callback: Callable[[str], Awaitable[None]] | None = None,
    ) -> AgentResult:
        plan = self.supervisor.plan(request)
        steps = [
            AgentStep(
                task_id="supervisor-1",
                agent="supervisor",
                action="plan",
                status="completed",
                summary=f"拆解为 {len(plan)} 个任务",
            )
        ]
        rag_result: dict[str, Any] | None = None
        action_result: dict[str, Any] | None = None

        for task in plan:
            if task.agent == "rag":
                rag_result = await self.rag_agent.run(request, session, tenant_id=tenant_id)
                steps.append(
                    AgentStep(
                        task_id=task.id,
                        agent="rag",
                        action=task.action,
                        status="completed" if rag_result.get("status") != "failed" else "failed",
                        summary=rag_result.get("summary", ""),
                        depends_on=task.depends_on,
                    )
                )
            elif task.agent == "action":
                action_result = await self.action_agent.run(
                    request,
                    task.action,
                    tenant_id=tenant_id,
                    user_id=user_id,
                )
                steps.append(
                    AgentStep(
                        task_id=task.id,
                        agent="action",
                        action=task.action,
                        status="completed" if action_result.get("status") == "completed" else "failed",
                        summary=action_result.get("summary", ""),
                        depends_on=task.depends_on,
                    )
                )

        if delta_callback:
            answer_parts: list[str] = []
            async for delta in self.chat_agent.stream(request.question, rag=rag_result, action=action_result):
                answer_parts.append(delta)
                await delta_callback(delta)
            answer = "".join(answer_parts)
        else:
            answer = await self.chat_agent.run(request.question, rag=rag_result, action=action_result)
        steps.append(
            AgentStep(
                task_id="chat-1",
                agent="chat",
                action="synthesize",
                status="completed",
                summary="已汇总专业 Agent 结果",
                depends_on=[task.id for task in plan if task.agent != "chat"],
            )
        )

        citations = (rag_result or {}).get("citations", [])
        tool_calls = (action_result or {}).get("tool_calls", [])
        artifacts = (action_result or {}).get("artifacts", [])
        approvals = (action_result or {}).get("approvals", [])
        status = "completed"
        if any(approval.status == "pending" for approval in approvals):
            status = "pending_approval"
        elif any(step.status == "failed" for step in steps):
            status = "partial"

        input_tokens = self.token_counter(request.question)
        output_tokens = self.token_counter(answer)
        return AgentResult(
            request_id=request_id,
            task_id=task_id,
            trace_id=trace_id,
            status=status,
            answer=answer,
            route=request.mode,
            model=self.model,
            citations=citations,
            agent_steps=steps,
            tool_calls=tool_calls,
            artifacts=artifacts,
            approvals=approvals,
            usage=TokenUsageSummary(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
        )
