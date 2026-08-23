from dataclasses import replace

from app.rag.context.context_builder import RagRuntimeContext


class ContextDegrader:
    """
    Context Overflow 时的降级策略。

    顺序：
    1. 删除相关性最低的 RAG Chunk
    2. 删除最旧的 Recent History
    """

    def degrade(
        self,
        context: RagRuntimeContext,
    ) -> RagRuntimeContext | None:
        if context.rag_chunks:
            return self._remove_lowest_ranked_rag_chunk(
                context
            )

        if context.history:
            return self._remove_oldest_history_message(
                context
            )

        return None

    def _remove_lowest_ranked_rag_chunk(
        self,
        context: RagRuntimeContext,
    ) -> RagRuntimeContext:
        new_chunks = context.rag_chunks[:-1]

        return replace(
            context,
            rag_chunks=new_chunks,
        )

    def _remove_oldest_history_message(
        self,
        context: RagRuntimeContext,
    ) -> RagRuntimeContext:
        new_history = context.history[1:]

        return replace(
            context,
            history=new_history,
        )