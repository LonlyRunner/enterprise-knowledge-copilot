from app.tools.registry import (
    create_tool_registry,
)

from app.services.business_gateway import (
    MockBusinessGateway,
)



def test_registry_register_query_order():

    registry = create_tool_registry(
        MockBusinessGateway()
    )


    tool = registry.get(
        "query_order"
    )


    assert tool is not None

    assert (
        tool.definition.name
        == "query_order"
    )



def test_registry_generate_schema():

    registry = create_tool_registry(
        MockBusinessGateway()
    )


    schemas = registry.schemas()


    assert len(schemas) == 3


    tool_names = [
        schema["function"]["name"]
        for schema in schemas
    ]


    assert "query_order" in tool_names

    assert "query_logistics" in tool_names

    assert "create_ticket" in tool_names