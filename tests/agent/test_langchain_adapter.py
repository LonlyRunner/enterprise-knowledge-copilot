from app.agent.langchain.adapters import (
    convert_to_langchain_tool,
)


from app.tools.registry import (
    create_tool_registry,
)


from app.services.business_gateway import (
    MockBusinessGateway,
)



def test_convert_query_order_tool():


    registry = create_tool_registry(
        MockBusinessGateway()
    )


    enterprise_tool = registry.get(
        "query_order"
    )


    langchain_tool = (
        convert_to_langchain_tool(
            enterprise_tool
        )
    )


    assert (
        langchain_tool.name
        ==
        "query_order"
    )


    assert (
        langchain_tool.description
        is not None
    )