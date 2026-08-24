class ReactAgent:
    def __init__(self, llm_client=None, tools=()):
        self.llm_client = llm_client
        self.tools = {tool.name: tool for tool in tools if hasattr(tool, "name")}

    async def run(self, question: str):
        if self.llm_client is None:
            return f"无法执行智能代理请求：{question}"
        state = []
        for _ in range(8):
            decision = await self.llm_client.chat(question)
            if getattr(decision, "type", None) == "tool":
                tool = self.tools.get(decision.tool_name)
                if tool is None:
                    return "请求的工具不存在。"
                result = await tool.execute(decision.input)
                state.append(result)
                question = f"{question}\n工具结果：{result}"
            else:
                return decision.answer
        return "智能代理达到最大执行步数。"
