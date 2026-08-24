import pytest


@pytest.mark.asyncio
async def test_rag_metrics(
    rag_service,
    conversation,
):


    result = await rag_service.chat(
        knowledge_base_id=(
            conversation.knowledge_base_id
        ),

        conversation_id=(
            conversation.id
        ),

        question=(
            "报销规则是什么？"
        ),
    )


    metrics = (
        result["metrics"]
    )


    assert (
        "trace_id"
        in metrics
    )


    assert (
        metrics["tokens"]
        is not None
    )


    assert (
        metrics["tokens"]["input"]
        > 0
    )


    assert (
        metrics["tokens"]["output"]
        > 0
    )