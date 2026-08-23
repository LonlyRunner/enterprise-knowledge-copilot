import json

from app.llm.base import BaseLLMClient
from app.llm.client import create_llm_client
from app.rag.models import DocumentChunk
from app.rag.rerankers.base import (
    BaseReranker,
    RerankResult,
)


class LLMReranker(BaseReranker):

    def __init__(
        self,
        llm_client: BaseLLMClient | None = None,
    ):
        self.llm_client = (
            llm_client
            or create_llm_client()
        )

    async def rerank(
        self,
        query: str,
        documents: list[DocumentChunk],
        top_k: int,
    ) -> list[RerankResult]:

        if not documents:
            return []

        document_text = "\n\n".join(
            (
                f"[{index}]\n"
                f"{document.content}"
            )
            for index, document
            in enumerate(documents)
        )

        prompt = f"""
你是一个文档相关性排序器。

你的任务是根据用户问题，对候选文档按照
“对回答该问题的帮助程度”进行排序。

用户问题：

{query}

候选文档：

{document_text}

要求：

1. 仔细判断数值范围、条件、时间、对象等限制。
2. 不要回答用户问题。
3. 只负责判断文档相关性。
4. 返回严格 JSON，不要输出 Markdown。
5. score 范围为 0 到 1。
6. index 必须对应候选文档编号。

返回格式：

[
  {{
    "index": 0,
    "score": 0.95
  }},
  {{
    "index": 1,
    "score": 0.60
  }}
]
""".strip()

        response = await self.llm_client.chat(
            prompt
        )

        raw_content = (
            response.content
            .strip()
        )

        # 防止模型偶尔返回 ```json ... ```
        if raw_content.startswith("```"):

            lines = raw_content.splitlines()

            lines = [
                line
                for line in lines
                if not line.strip().startswith(
                    "```"
                )
            ]

            raw_content = "\n".join(
                lines
            )

        try:
            data = json.loads(
                raw_content
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Reranker returned invalid JSON: "
                f"{raw_content}"
            ) from exc

        results: list[
            RerankResult
        ] = []

        seen_indexes: set[int] = set()

        for item in data:

            index = int(
                item["index"]
            )

            score = float(
                item["score"]
            )

            if (
                index < 0
                or index >= len(documents)
            ):
                continue

            if index in seen_indexes:
                continue

            seen_indexes.add(
                index
            )

            score = max(
                0.0,
                min(
                    score,
                    1.0,
                ),
            )

            results.append(
                RerankResult(
                    chunk=documents[index],
                    score=score,
                    original_rank=index + 1,
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:top_k]