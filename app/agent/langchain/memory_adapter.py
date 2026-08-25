from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)


class ConversationMemoryAdapter:
    """
    企业Conversation Memory

    Database Message

        ↓

    LangChain Message
    """


    def __init__(
        self,
        conversation_service,
    ):

        self.conversation_service = (
            conversation_service
        )


    async def load_history(
        self,
        *,
        knowledge_base_id,
        conversation_id,
    ):

        detail = await (
            self.conversation_service
            .get_detail(
                knowledge_base_id=(
                    knowledge_base_id
                ),

                conversation_id=(
                    conversation_id
                ),
            )
        )


        messages = []


        for message in (
            detail["messages"]
        ):


            if message.role == "user":

                messages.append(
                    HumanMessage(
                        content=(
                            message.content
                        )
                    )
                )


            elif (
                message.role
                ==
                "assistant"
            ):

                messages.append(
                    AIMessage(
                        content=(
                            message.content
                        )
                    )
                )


        return messages