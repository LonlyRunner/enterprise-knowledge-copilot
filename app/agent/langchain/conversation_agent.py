from langchain_core.messages import HumanMessage


class ConversationAgent:


    def __init__(
        self,
        agent,
        memory_adapter,
    ):

        self.agent = agent

        self.memory_adapter = (
            memory_adapter
        )



    async def run(
        self,
        *,
        question,
        knowledge_base_id,
        conversation_id,
    ):


        history = await (
            self.memory_adapter
            .load_history(
                knowledge_base_id=(
                    knowledge_base_id
                ),

                conversation_id=(
                    conversation_id
                ),
            )
        )


        messages = history + [
            HumanMessage(
                content=question
            )
        ]


        result = await (
            self.agent
            .ainvoke(
                {
                    "messages":
                    messages
                }
            )
        )


        return result