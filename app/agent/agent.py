import json


class NativeAgent:


    def __init__(
        self,
        llm,
        executor,
        registry,
        max_steps=5,
    ):
        self.llm = llm
        self.executor = executor
        self.registry = registry
        self.max_steps = max_steps

    async def run(
            self,
            question,
            *,
            tenant_id,
            user_id,
            trace_id,
    ):

        messages = [
            {
                "role": "user",
                "content": question,
            }
        ]

        for step in range(
                self.max_steps
        ):

            response = await self.llm.chat_with_tools(
                messages,
                self.registry.schemas(),
            )

            messages.append(
                {
                    "role":
                        "assistant",

                    "content":
                        response.content,

                }
            )

            if not response.tool_calls:
                return {
                    "answer":
                        response.content,

                    "steps":
                        step + 1,
                }

            for call in response.tool_calls:
                result = await self.executor.execute(

                    call.name,

                    call.arguments,

                    tenant_id=tenant_id,

                    user_id=user_id,

                    trace_id=trace_id,

                )

                messages.append(

                    {

                        "role":
                            "tool",

                        "tool_call_id":
                            call.id,

                        "name":
                            call.name,

                        "content":
                            json.dumps(
                                result,
                                ensure_ascii=False,
                            ),

                    }

                )

        return {

            "answer":
                "执行超过最大步骤",

            "steps":
                self.max_steps,

        }



class ReactAgent:
    """
    旧版 Agent 兼容入口

    保留旧测试和旧代码调用方式。

    新代码使用 NativeAgent。
    """

    def __init__(
        self,
        tools=None,
        **kwargs,
    ):

        self.tools = tools or []


    async def run(
        self,
        question,
        **kwargs,
    ):

        """
        兼容旧测试

        暂时模拟旧 Tool 行为
        """

        for tool in self.tools:

            if tool is None:
                continue

            if not hasattr(tool, "execute"):
                continue

            result = await tool.execute(
                question
            )

            if result:

                return {
                    "answer": result
                }


        return {
            "answer":
            "无法处理该问题"
        }
