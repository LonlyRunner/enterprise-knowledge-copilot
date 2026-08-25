from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from app.gateway.schemas import GatewayRequest


@dataclass
class PlannedTask:
    id: str
    agent: Literal["rag", "action", "chat"]
    action: str
    depends_on: list[str] = field(default_factory=list)


class SupervisorAgent:
    """Break a user request into bounded specialist tasks."""

    ACTION_WORDS = ("订单", "物流", "工单", "售后", "销售", "异常", "审批", "退款", "CRM")
    RAG_WORDS = ("制度", "规则", "合同", "政策", "规范", "知识库", "根据", "销售")

    def plan(self, request: GatewayRequest) -> list[PlannedTask]:
        tasks: list[PlannedTask] = []
        question = request.question

        need_action = request.mode == "agent" or any(word in question for word in self.ACTION_WORDS)
        need_rag = request.mode == "rag" or (
            request.knowledge_base_id is not None
            and (request.mode in {"auto", "agent"} or any(word in question for word in self.RAG_WORDS))
        )

        if request.mode == "chat":
            need_action = False
            need_rag = False

        if need_rag:
            tasks.append(PlannedTask(id="rag-1", agent="rag", action="knowledge_search"))
        if need_action:
            tasks.append(PlannedTask(id="action-1", agent="action", action=self._action_name(question)))

        dependencies = [task.id for task in tasks]
        tasks.append(PlannedTask(id="chat-1", agent="chat", action="synthesize", depends_on=dependencies))
        return tasks

    @staticmethod
    def _action_name(question: str) -> str:
        if "销售" in question or "报告" in question:
            return "analyze_sales"
        if "工单" in question or "售后" in question:
            return "handle_ticket"
        if "物流" in question:
            return "query_logistics"
        return "query_order"

