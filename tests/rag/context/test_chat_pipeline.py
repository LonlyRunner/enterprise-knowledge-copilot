import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_chat_pipeline(
    rag_service,
):

    conversation_id = 'eef2798e-2dd4-446b-9a9d-d10fc227cb6c'

    knowledge_base_id = '1c64f8eb-aefe-4be8-b608-aa59a09e42a8'


    result = await rag_service.chat(
        knowledge_base_id=(
            knowledge_base_id
        ),
        conversation_id=(
            conversation_id
        ),
        question=(
            "公司的报销流程是什么？"
        ),
    )


    assert result is not None

    assert "answer" in result

    assert (
        result["conversation_id"]
        ==
        conversation_id
    )