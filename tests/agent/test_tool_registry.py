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


    assert len(schemas) == 1


    assert (
        schemas[0]["function"]["name"]
        == "query_order"
    )