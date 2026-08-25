import pytest


from app.agent.langchain.adapters import (
    convert_to_langchain_tool,
)


from app.tools.registry import (
    create_tool_registry,
)


from app.services.business_gateway import (
    MockBusinessGateway,
)



def test_convert_tool():


    registry = create_tool_registry(
        MockBusinessGateway()
    )


    tool = registry.get(
        "query_order"
    )


    lc_tool = convert_to_langchain_tool(
        tool
    )


    assert (
        lc_tool.name
        ==
        "query_order"
    )


    assert (
        lc_tool.description
        is not None
    )