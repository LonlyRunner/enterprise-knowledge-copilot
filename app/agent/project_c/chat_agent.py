from __future__ import annotations

import json
from typing import Any

from app.contracts import AgentArtifact, AgentCitation, ApprovalRequest
from app.llm.base import BaseLLMClient


class ProjectCChatAgent:
    def __init__(self, llm: BaseLLMClient | None = None):
        self.llm = llm

    async def run(self, question: str, *, rag: dict[str, Any] | None, action: dict[str, Any] | None) -> str:
        if action and action.get("status") == "pending_approval":
            return (
                f"{action.get('summary', '业务操作需要审批')}。"
                "请在审批完成后重新提交 approve_actions=true 的请求。"
            )

        if self.llm is not None:
            context = {
                "question": question,
                "knowledge": rag or {},
                "business": action or {},
            }
            prompt = (
                "你是星云科技 Chat Agent。请根据以下已完成的 RAG 和业务 Agent 结果回答用户。"
                "不要虚构工具没有返回的数据；报告要有结论、异常和下一步。"
                f"\n上下文：{json.dumps(context, ensure_ascii=False, default=str)[:12000]}"
            )
            try:
                result = await self.llm.chat(prompt)
                return result.content
            except Exception:
                # The Gateway still returns a useful deterministic response when
                # the model provider is temporarily unavailable.
                pass

        sections = []
        if rag and rag.get("answer"):
            sections.append(f"知识库结论：{rag['answer']}")
        if action:
            sections.append(f"业务处理：{action.get('summary', '')}")
            data = action.get("data") or {}
            if data.get("order_count") is not None:
                sections.append(
                    f"销售概览：共 {data['order_count']} 个订单，"
                    f"金额 {data.get('total_amount', 0):,.2f} {data.get('currency', 'CNY')}；"
                    f"异常订单 {len(data.get('anomaly_orders', []))} 个。"
                )
        return "\n".join(sections) or "已收到请求，但当前没有可返回的业务结果。"

    async def stream(self, question: str, *, rag: dict[str, Any] | None, action: dict[str, Any] | None):
        """Yield answer deltas; deterministic mode uses the same contract for local tests."""
        if self.llm is None:
            answer = await self.run(question, rag=rag, action=action)
            for index in range(0, len(answer), 24):
                yield answer[index:index + 24]
            return
        context = {"question": question, "knowledge": rag or {}, "business": action or {}}
        prompt = "你是星云科技 Chat Agent。请根据以下已完成的 RAG 和业务 Agent 结果回答用户，不要虚构数据。\n" + json.dumps(context, ensure_ascii=False, default=str)[:12000]
        try:
            async for delta in self.llm.stream_chat(prompt):
                yield delta
        except Exception:
            answer = await self.run(question, rag=rag, action=action)
            for index in range(0, len(answer), 24):
                yield answer[index:index + 24]
