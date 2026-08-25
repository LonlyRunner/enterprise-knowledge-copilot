from app.agent.langchain.llm_adapter import (
    DeepSeekChatAdapter,
)


from app.llm.base import (
    LLMMessage,
)



def test_adapter_type():

    adapter = DeepSeekChatAdapter(
        client=None
    )


    assert (
        adapter._llm_type
        ==
        "deepseek"
    )