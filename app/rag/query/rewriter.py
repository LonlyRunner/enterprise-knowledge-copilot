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
        history: list[dict],
    ) -> str:

        if not history:
            return question

        history_text = "\n".join(
            (
                f"{item['role']}: "
                f"{item['content']}"
            )
            for item in history
        )

        prompt = f"""
你是企业知识库系统中的查询改写模块。

你的任务不是回答用户问题。

你的任务是根据对话历史，把用户最新问题改写成一个：
完整、独立、适合知识库检索的问题。

要求：

1. 补全最新问题中缺失的上下文。
2. 保留金额、时间、人员、制度名称等关键条件。
3. 不要增加对话中不存在的事实。
4. 不要回答问题。
5. 如果最新问题本身已经完整，尽量保持原意。
6. 只输出改写后的问题，不要解释。

对话历史：

{history_text}

用户最新问题：

{question}
""".strip()

        result = await self.llm_client.chat(
            prompt
        )

        rewritten = (
            result.content
            .strip()
        )

        if not rewritten:
            return question

        return rewritten