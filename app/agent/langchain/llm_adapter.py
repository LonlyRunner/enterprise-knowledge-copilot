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


from langchain_core.tools import BaseTool

from langchain_core.messages import (
    ToolMessage,
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
        """
        LangChain Tool Calling入口

        tools:
            StructuredTool列表
        """

        self.bound_tools = tools

        return self