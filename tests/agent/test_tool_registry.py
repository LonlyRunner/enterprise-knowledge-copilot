from app.tools.registry import (
    create_tool_registry,
)


def test_registry_register_query_order():

    registry = create_tool_registry()

    tool = registry.get(
        "query_order"
    )

    assert tool is not None

    assert (
        tool.name
        == "query_order"
    )


def test_registry_generate_schema():

    registry = create_tool_registry()

    schemas = registry.schemas()

    assert len(schemas) == 1

    schema = schemas[0]

    assert (
        schema["type"]
        == "function"
    )

    assert (
        schema["function"]["name"]
        == "query_order"
    )