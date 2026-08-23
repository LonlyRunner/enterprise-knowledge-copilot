from app.llm.base import BaseLLMClient
from app.llm.client import create_llm_client


class QueryRewriter:

    def __init__(
        self,
        llm_client: BaseLLMClient | None = None,
    ):
        self.llm_client = (
            llm_client
            or create_llm_client()
        )

    async def rewrite(
            self,
            question: str,
            history,
            summary: str | None = None,
    ) -> str:
        summary_text = (
                summary
                or "暂无会话摘要。"
        )

        history_text = "\n".join(
            (
                f"{message['role']}: "
                f"{message['content']}"
            )
            for message in history
        )

        prompt = f"""
    你负责将多轮对话中的当前问题改写成一个可以独立理解的问题。

    会话长期摘要：

    {summary_text}

    最近对话历史：

    {history_text}

    当前用户问题：

    {question}

    要求：

    1. 消除“这个”“那个”“前面说的”等指代。
    2. 保留金额、人员、时间、条件等关键信息。
    3. 不添加会话中不存在的事实。
    4. 如果当前问题已经可以独立理解，则保持原意。
    5. 只输出改写后的问题。
    """.strip()

        result = (
            await self.llm_client.chat(
                prompt
            )
        )

        return result.content.strip()