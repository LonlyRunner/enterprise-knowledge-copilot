from collections.abc import Sequence
from typing import Protocol

from app.llm.base import BaseLLMClient


class MessageLike(Protocol):
    role: str
    content: str


class ConversationSummarizer:

    def __init__(
        self,
        llm_client: BaseLLMClient,
    ) -> None:

        self.llm_client = llm_client

    async def summarize(
        self,
        messages: Sequence[MessageLike],
        existing_summary: str | None = None,
    ) -> str:

        if not messages:
            return existing_summary or ""

        history_text = (
            self._format_messages(
                messages
            )
        )

        prompt = self._build_prompt(
            history_text=history_text,
            existing_summary=existing_summary,
        )

        summary = await self._call_llm(
            prompt
        )

        return summary.strip()

    def _format_messages(
        self,
        messages: Sequence[MessageLike],
    ) -> str:

        lines: list[str] = []

        for message in messages:

            role = (
                message.role.upper()
            )

            lines.append(
                f"{role}: {message.content}"
            )

        return "\n".join(
            lines
        )

    def _build_prompt(
        self,
        history_text: str,
        existing_summary: str | None,
    ) -> str:

        existing = (
            existing_summary
            or "暂无已有摘要。"
        )

        return f"""
你是一个企业知识库问答系统的会话摘要器。

你的任务是压缩历史对话，同时保留后续多轮问答真正需要的信息。

必须保留：
1. 用户明确提出的问题和需求。
2. 已经确认的重要事实。
3. 金额、时间、人员、条件、规则等关键实体。
4. 用户问题中的指代关系和上下文。
5. 尚未解决的问题。
6. 对后续 Query Rewrite 有帮助的信息。

不要：
1. 添加对话中不存在的信息。
2. 推测企业制度内容。
3. 把 RAG 检索结果之外的知识当作事实。
4. 写无关的寒暄内容。

已有会话摘要：

{existing}

需要合并进摘要的新历史：

{history_text}

请输出新的简洁会话摘要。
""".strip()

    async def _call_llm(
        self,
        prompt: str,
    ) -> str:

        result = (
            await self.llm_client.chat(
                prompt
            )
        )

        return result.content