from typing import Any, Iterator

from langchain_core.language_models.chat_models import (
    BaseChatModel,
)

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)

from langchain_core.outputs import (
    ChatGeneration,
    ChatResult,
)


class DeepSeekChatAdapter(
    BaseChatModel
):
    """
    DeepSeekLLMClient

    ->

    LangChain BaseChatModel
    """

    client: Any

    def _generate(
            self,
            messages,
            stop=None,
            run_manager=None,
            **kwargs,
    ):
        raise NotImplementedError(
            "同步调用未实现，请使用异步"
        )

    async def _agenerate(
            self,
            messages,
            stop=None,
            run_manager=None,
            **kwargs,
    ):
        last_message = messages[-1]

        result = await self.client.chat(
            last_message.content
        )

        message = AIMessage(
            content=result.content
        )

        generation = ChatGeneration(
            message=message
        )

        return ChatResult(
            generations=[
                generation
            ]
        )

    @property
    def _llm_type(self):
        return "deepseek"