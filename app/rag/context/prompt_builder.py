from dataclasses import dataclass
from typing import Protocol


class MessageLike(Protocol):
    role: str
    content: str


class ChunkLike(Protocol):
    content: str


@dataclass(frozen=True)
class BuiltPrompt:
    system_prompt: str
    user_prompt: str


class PromptBuilder:
    """
    最终回答阶段 Prompt Builder。

    负责统一组织：
    - Conversation Summary
    - Recent History
    - RAG Context
    - Current Question

    不负责：
    - Retrieval
    - Token Selection
    - LLM 调用
    """

    def build_answer_prompt(
        self,
        *,
        summary: str | None,
        history: list[MessageLike],
        rag_chunks: list[ChunkLike],
        question: str,
    ) -> BuiltPrompt:
        system_prompt = self._build_system_prompt()

        summary_text = self._format_summary(summary)
        history_text = self._format_history(history)
        rag_context_text = self._format_rag_context(rag_chunks)

        user_prompt = f"""
## Conversation Summary
{summary_text}

## Recent Conversation
{history_text}

## Retrieved Knowledge
{rag_context_text}

## Current Question
{question}

请基于 Retrieved Knowledge 回答用户问题。

要求：
1. 企业制度、流程、金额、审批规则等事实必须以 Retrieved Knowledge 为依据。
2. Conversation Summary 和 Recent Conversation 仅用于理解上下文、指代和用户意图。
3. 如果 Retrieved Knowledge 不足以回答，请明确说明信息不足。
4. 不要编造知识库中不存在的制度或事实。
5. 回答应直接、清晰。
""".strip()

        return BuiltPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _build_system_prompt(self) -> str:
        return """
你是一个企业知识库 RAG 助手。

你的主要任务是：
根据检索到的企业知识回答用户问题。

你必须区分：
- Conversation Context：用于理解用户在问什么。
- Retrieved Knowledge：用于确定事实答案。

不得将会话摘要或历史消息中的未经知识库确认的信息，
直接作为企业事实回答。
""".strip()

    def _format_summary(
        self,
        summary: str | None,
    ) -> str:
        if not summary:
            return "暂无会话摘要。"

        return summary

    def _format_history(
        self,
        history: list[MessageLike],
    ) -> str:
        if not history:
            return "暂无最近对话历史。"

        return "\n".join(
            f"{message.role}: {message.content}"
            for message in history
        )

    def _format_rag_context(
        self,
        rag_chunks: list[ChunkLike],
    ) -> str:
        if not rag_chunks:
            return "未检索到可用知识。"

        sections: list[str] = []

        for index, chunk in enumerate(
            rag_chunks,
            start=1,
        ):
            sections.append(
                f"[Knowledge {index}]\n{chunk.content}"
            )

        return "\n\n".join(sections)