from app.tools.order import QueryOrderTool

from app.services.business_gateway import (
    MockBusinessGateway,
)


def test_query_order_schema():

    tool = QueryOrderTool(
        MockBusinessGateway()
    )

    assert (
        tool.definition.name
        == "query_order"
    )

    assert (
        tool.definition.side_effect
        is False
    )

    assert (
        tool.definition.requires_approval
        is False
    )


def test_query_order_required_argument():

    tool = QueryOrderTool(
        MockBusinessGateway()
    )

    schema = (
        tool.definition.input_schema
    )

    assert (
        "order_id"
        in schema["required"]
    )

    assert (
        schema["additionalProperties"]
        is False
    )