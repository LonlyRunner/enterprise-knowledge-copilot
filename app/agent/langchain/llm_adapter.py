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

from pydantic import Field
from langchain_core.tools import BaseTool

from langchain_core.messages import (
    ToolMessage,
)
import logging

logger = logging.getLogger(__name__)


class DeepSeekChatAdapter(
    BaseChatModel
):
    """
    DeepSeekLLMClient

    ->

    LangChain BaseChatModel
    """

    client: Any

    bound_tools: list = Field(
        default_factory=list
    )

    def _generate(
            self,
            messages,
            stop=None,
            run_manager=None,
            **kwargs,
    ):

        logger.debug("deepseek_langchain_generate")

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            self._agenerate(
                messages,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            )
        )

        return result

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

        tool_calls = []

        if hasattr(
                result,
                "tool_calls"
        ):

            for call in result.tool_calls:
                tool_calls.append(

                    {

                        "id":
                            call.id,

                        "name":
                            call.name,

                        "args":
                            call.arguments,

                    }

                )

        message = AIMessage(

            content=result.content,

            tool_calls=tool_calls,

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

    def bind_tools(
            self,
            tools,
            **kwargs,
    ):

        return self.model_copy(
            update={
                "bound_tools": tools
            }
        )
        """
        LangChain Tool Calling入口

        tools:
            StructuredTool列表
        """

        self.bound_tools = tools

        return self
